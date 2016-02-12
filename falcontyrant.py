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

class FalconTyrant(Peer):
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

        #dj
        #uj = bandwidth/#peers           
    
        uploads = []
        if len(requests) == 0:
            logging.debug("No one wants my pieces!")
            chosen = []
            bws = []
        else:
            logging.debug("Still here: uploading to a random peer")
            # change my internal state for no reason
            self.dummy_state["cake"] = "pie"

            raitoList = []
            if round == 0:
                dArray = []
                uArray = []
                estimatedSlots = 4
                for i in range(len(peers)):
                    uArray.append(self.up_bw/(len(peers)-1))

                #default = 1
                for i in range(len(peers)):
                    dArray.append(peers[i].up_bw/estimatedSlots)

            
                for i in range(len(peers)):
                    ratioList.append((float(dArray[i]/uArray[i]),peers[i].id))

                #ratioList = random.shuffle(ratioList)

                for peer in peers:
                    uploads.append(Upload(self.id, peer.id,
                                          self.up_bw/len(peers)))
                    

            if round != 0:
                

                # download history 
                prevDownloadHistory = history.downloads[round-1]
                historyDownDict = dict()

                for downLoad in prevDownloadHistory:
                    fromId = downLoad.from_id
                    if fromId not in historyDownDict.keys():
                        historyDownDict[fromId] = downLoad.blocks
                    else:
                        historyDownDict[fromId] += downLoad.blocks


                # upload history
                prevUploadHistory = history.uploads[round-1]
                historyUpDict = dict()

                for upLoad in prevUploadHistory:
                    toId = upLoad.to_id
                    if toId not in historyUpDict.keys():
                        historyUpDict[toId] = upLoad.bw
                    else:
                        historyUpDict[toId] += upLoad.bw

                duDict = dict()                       
                for peer in peers:
                    if (peer.id in historyDownDict.keys()):
                        prevDown = historyDownDict[peer.id]
                        # what if I didn't upload to j
                        #if(peer.id in historyUpDict.keys():
                        prev3rounds = [False, False, False]
                        if round >= 3:                           
                            for i in range(3):
                                dowHis = history.downloads[round-i-1]
                                for down in dowHis:
                                    if peer.id == down.from_id:
                                        prev3rounds[i] = True
           
                        if peer.id not in historyUpDict.keys():
                            prevUp = self.up_bw/(len(peers)-1)
                        else:
                            prevUp = historyUpDict[peer.id]
                            
                        if (prev3rounds[0]==True) and (prev3rounds[1]==True) \
                           and prev3rounds[2]==True:
                            prevUp = (1-0.1)*prevUp
                            
                        duDict[peer.id] = [prevDown, prevUp]
                    else:
                        
                        prevDown = len(peer.available_pieces)/round/4
  
                        if peer.id not in historyUpDict.keys():
                            prevUp = self.up_bw/(len(peers)-1)
                        else:
                            prevUp = historyUpDict[peer.id]*(1+0.2)
                        duDict[peer.id] = [prevDown, prevUp]

                rankList = []
                for peer in duDict.keys():
                    rankList.append((float(duDict[peer][0]/duDict[peer][1]),
                                     duDict[peer][1], peer))

                rankList.sort()
                rankList.reverse()

                cap = self.up_bw
                count = 0
                while cap > 0:
                    if (count <= len(rankList)-1):
                        if (cap - rankList[count][1])> 1:
                            uploads.append(Upload(self.id, rankList[count][2],
                                                  rankList[count][1]))
                        cap = cap - rankList[count][1]
                        count += 1
                    else:
                        break
            
        return uploads
