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
                if piece not in av_count_dic.keys():
                    av_count_dic[piece] = [1, [peer.id]]
                else:
                    av_count_dict[piece][0] += 1
                    av_count_dict[piece][1].append(peer.id)

        for peer in peers:
            av_set = set(peer.available_pieces)
            
            isect = av_set.intersection(np_set)

            if self.max_requests >= len(isect):
                for piece_id in isect:
                    start_block = self.pieces[piece_id]
                    r = Request(self.id, peer.id, piece_id, start_block)
                    request.append(r)

            else:
                isect_list = []

                for isectPiece in isect:
                    isect_list.append((av_count_dict[isectPiece][0], isectPiece))

                isect_list.sort()

                rarestCount = isect_list[0][0]
                sameRareList =[]
                for el in isect_list:
                    if el[0] == rarestCount:
                        sameRareList.append(el[1])
                random.shuffle(sameRareList)

                listSecond = []
                for p in isect_list[len(el):]:
                    listSecond.append(p[1])
                isectIDList = sameRareList + listSecond
                isectIDList = isectIDList[:self.max_requests]
                for piece_id in isectIDList:
                    start_block = self.pieces[piece_id]
                    r = Request(self.id, peer.id. piece_id, start_block)
                    requests.append(r)
 
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
                for i in range(len(peers)):
                    uArray.append(self.up_bw/len(peers))

                udefault = 1
                for i in range(len(peers)):
                    dArray.append(udefault)

            
                for i in range(len(peers)):
                    ratioList.append((float(dArray[i]/uArray[i]),peers[i].id))

                #ratioList = random.shuffle(ratioList)

                for peer in peers:
                    uploads.append(Upload(self.id, peer.id,
                                          self.up_bw/len(peers)))
                    

            if round != 0:
                prevDownloadHistory = history.downloads[round-1]

                for peer in peers:
                if peer.id in prevDownloadHistory.keys():
                    for selectedPeer in prevDownloadHistory:
                        if selectedPeer.id = peer.id:
                            dj = dj + selectedPeer.blocks
                    if(round >= 3):
                        if peer.id in history.download[round-2]:
                            if peer.id in history.download[round-3]:
                        
                                uj = (1-0.1)*uj  
                    else uj = uj
                    
                            
                else:
                    dj = peer.available_pieces/ (round-1)
                    uj = (1+0.2) * uj
                dArray.append(dj)
                uArray.append(uj)
                ratioArray.append(dj/uj)
                
            capi = self.up_bw
            rationArray.sort();
            while(capi> 0){
        
            #request = random.choice(requests)
            #chosen = [request.requester_id]
            # Evenly "split" my upload bandwidth among the one chosen requester
            #bws = even_split(self.up_bw, len(chosen))

        # create actual uploads out of the list of peer ids and bandwidths
        #uploads = [Upload(self.id, peer_id, bw)
                   #for (peer_id, bw) in zip(chosen, bws)]
            
        return uploads
