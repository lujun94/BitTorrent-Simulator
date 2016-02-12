#!/usr/bin/python

# This is a dummy peer that just illustrates the available information your peers 
# have available.

# You'll want to copy this file to AgentNameXXX.py for various versions of XXX,
# probably get rid of the silly logging messages, and then add more logic.

import random
import logging

from messages import Upload, Request
from util import even_split
from peer import Peer

class FalconTourney(Peer):
    def post_init(self):
        print "post_init(): %s here!" % self.id
        self.dummy_state = dict()
        self.dummy_state["cake"] = "lie"
    
    def requests(self, peers, history):
        """
        peers: available info about the peers (who has what pieces)
        history: what's happened so far as far as this peer can see

        returns: a list of Request() objects

        This will be called after update_pieces() with the most recent state.
        """
        needed = lambda i: self.pieces[i] < self.conf.blocks_per_piece
        needed_pieces = filter(needed, range(len(self.pieces)))
        np_set = set(needed_pieces)  # sets support fast intersection ops.


        logging.debug("%s here: still need pieces %s" % (
            self.id, needed_pieces))

        logging.debug("%s still here. Here are some peers:" % self.id)
        for p in peers:
            logging.debug("id: %s, available pieces: %s" % (p.id, p.available_pieces))

        logging.debug("And look, I have my entire history available too:")
        logging.debug("look at the AgentHistory class in history.py for details")
        logging.debug(str(history))

        requests = []   # We'll put all the things we want here
        # Symmetry breaking is good...
        random.shuffle(needed_pieces)
        
        # Sort peers by id.  This is probably not a useful sort, but other 
        # sorts might be useful
        peers.sort(key=lambda p: p.id)
        # request all available pieces from all peers!
        # (up to self.max_requests from each)
        av_count_dict = dict()
        for peer in peers:
            av_set = set(peer.available_pieces)
            for piece in av_set:
                if piece not in av_count_dict.keys():
                    av_count_dict[piece] = [1, [peer.id]]
                else:
                    av_count_dict[piece][0] += 1
                    av_count_dict[piece][1].append(peer.id)
        
        for peer in peers:
            # pieces that peer has
            av_set = set(peer.available_pieces)
            # intersection between what user needs and what other peers have
            isect = av_set.intersection(np_set)
            
            # can send all the request in this round
            if self.max_requests >= len(isect):
                # write request message to right peers
                for piece_id in isect:
                    start_block = self.pieces[piece_id]
                    r = Request(self.id, peer.id, piece_id, start_block)
                    requests.append(r)
                    
            # pick rarest-first                    
            else:
                isect_list = []
                # number of peers who have this piece and what piece
                for isectPiece in isect:
                    isect_list.append((av_count_dict[isectPiece][0],isectPiece))

                # sort according to first index, which is # of peers who own it
                isect_list.sort()
                # the fewer peers have the piece, the rarer the piece is
                # find the  # of people who own the rarest piece 
                rarestCount = isect_list[0][0]
                sameRareList = []
                # find all equally rarest pieces
                for el in isect_list:
                    if el[0] == rarestCount:
                        sameRareList.append(el[1])
                # make sure the order is random        
                random.shuffle(sameRareList)
                
                listSecond = []
                # merge shuffled rarest list and the rest together
                for p in isect_list[len(el):]:
                    listSecond.append(p[1])
                isectIDList = sameRareList + listSecond
                # cut the list and get needed amount of peers'ID
                isectIDList = isectIDList[:self.max_requests]
                # write request message to right peers 
                for piece_id in isectIDList:
                    start_block = self.pieces[piece_id]
                    r = Request(self.id, peer.id, piece_id, start_block)
                    requests.append(r)
            # More symmetry breaking -- ask for random pieces.
            # This would be the place to try fancier piece-requesting strategies
            # to avoid getting the same thing from multiple peers at a time.

            #for piece_id in random.sample(isect, n):
                # aha! The peer has this piece! Request it.
                # which part of the piece do we need next?
                # (must get the next-needed blocks in order)
                #start_block = self.pieces[piece_id]
                #r = Request(self.id, peer.id, piece_id, start_block)
                #requests.append(r)

        return requests
    
    def uploads(self, requests, peers, history):
        """
        requests -- a list of the requests for this peer for this round
        peers -- available info about all the peers
        history -- history for all previous rounds

        returns: list of Upload objects.

        In each round, this will be called after requests().
        """
        round = history.current_round()
        logging.debug("%s again.  It's round %d." % (
            self.id, round))
        # One could look at other stuff in the history too here.
        # For example, history.downloads[round-1] (if round != 0, of course)
        # has a list of Download objects for each Download to this peer in
        # the previous round.

        if round >= 2:
            # collect the history of download round>=2
            prevDownHistory = history.downloads[round-1]
            prevDownHistory2 = history.downloads[round-2]
            historyDict = dict()
            
            #go through the history of round - 1
            for downLoad in prevDownHistory:
                fromId = downLoad.from_id
                if fromId not in historyDict.keys():
                    historyDict[fromId] = downLoad.blocks
                else:
                    historyDict[fromId] += downLoad.blocks
                    
            #go through the history of round - 2
            for downLoad in prevDownHistory2:
                fromId = downLoad.from_id
                if fromId not in historyDict.keys():
                    historyDict[fromId] = downLoad.blocks
                else:
                    historyDict[fromId] += downLoad.blocks


        rankSlotsNum = 2
        if int(len(peers)/6) > 2:
            rankSlotNum = int(len(peers)/6)
            
        optiSlotNum = 1
        if int(len(peers)/12) > 1:
            optiSlotNum = int(len(peers)/12)
        totalSlotNum = rankSlotsNum + optiSlotNum
        if len(requests) == 0:
            logging.debug("No one wants my pieces!")
            chosen = []
            bws = []
        else:
            #logging.debug("Still here: uploading to a random peer")
            # change my internal state for no reason
            self.dummy_state["cake"] = "pie"

            chosen = []
            if round < 2:
                #randomly choose peers for unchoking slots
                requesterList = []
                for request in requests:
                    if request.requester_id not in requesterList:
                        requesterList.append(request.requester_id)
                            
                for i in range(totalSlotNum):
                    if len(requests) != 0:
                        randomRequester = random.choice(requesterList)
                        chosen.append(randomRequester)
                        requesterList.remove(randomRequester)                   

            else:
                # select the top 3 to be in the unchoking slots
                requesterList = []
                for request in requests:
                    if request.requester_id not in requesterList:
                        requesterList.append(request.requester_id)

                rankList = []
                for requester in requesterList:
                    if requester not in historyDict.keys():
                        rankList.append((0, requester))
                    else:
                        rankList.append((historyDict[requester], requester))

                tempChosen = []
                randomSlotLeft = rankSlotsNum
                if len(rankList) <= rankSlotsNum:
                    for el in rankList:
                        tempChosen.append(el[1])
                    randomSlotLeft = rankSlotsNum - len(rankList)
                else:
                    rankList.sort()
                    rankList.reverse()
                    rankList = rankList[:rankSlotsNum]
                    for el in rankList:
                        tempChosen.append(el[1])
                    randomSlotLeft = 0

                for request in requests:
                    if request.requester_id in tempChosen:
                        requests.remove(request)
           
                #If rank slots aren't fill, random pick a peers to the slot
                for i in range(randomSlotLeft):
                    if len(requests) != 0:
                        randomRequest = random.choice(requests)
                        tempChosen.append(randomRequest.requester_id)
                        requests.remove(randomRequest)

                # get history of last round
                prevUpHistory = history.uploads[round-1]
                for i in range(len(prevUpHistory)):
                    chosen.append(prevUpHistory[i].to_id)

                if round%3 != 0:
                    # if the slots are full last round, copy all the slots
                    if len(chosen) == totalSlotNum:
                        for i in range(len(tempChosen)):
                            chosen[i]= tempChosen[i]
                    else:
                        # if last round's optimistic unchoking is not
                        # chosen this round
                        prevchosen = chosen
                        if len(chosen) >= optiSlotNum:
                            chosen = []
                            for i in range(len(tempChosen)):
                                chosen.append(tempChosen[i])
                            for i in range(optiSlotNum):
                                if prevchosen[-optiSlotNum+i] not in tempChosen:
                                    # copy optimistic unchoking from last round
                                    last = prevchosen[-optiSlotNum+i]
                                    chosen.append(last)
                                else:
                                    if len(requests) != 0:
                                        randomRequest = random.choice(requests)
                                        chosen.append(randomRequest.requester_id)
                                        requests.remove(randomRequest)
                                    
                        # if last round's slots are all empty
                        else:
                            chosen = []
                            for i in range(len(tempChosen)):
                                chosen.append(tempChosen[i])
                            # add random peer to this extra slot                              
                            for i in range(totalSlotNum-len(tempChosen)):
                                if len(requests) != 0:
                                    randomRequest = random.choice(requests)
                                    chosen.append(randomRequest.requester_id)
                                    requests.remove(randomRequest)
                else:
                    chosen = []
                    chosen = tempChosen
                    if len(requests) != 0:
                        randomRequest = random.choice(requests)
                        # select optimistic unchoking
                        chosen.append(randomRequest.requester_id)                   
                                       
                                       
            #request = random.choice(requests)
            #chosen = [request.requester_id]
            # Evenly "split" my upload bandwidth among the one chosen requester
            bws = even_split(self.up_bw, len(chosen))

        # create actual uploads out of the list of peer ids and bandwidths
        uploads = [Upload(self.id, peer_id, bw)
                   for (peer_id, bw) in zip(chosen, bws)]
            
        return uploads

