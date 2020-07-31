import numpy as np
import time
import heapq
from sklearn.metrics.pairwise import cosine_similarity


class Summarizer:
    def __init__(self, reviews, vectorizer, budget=200):
        self.reviews = reviews
        self.vectorizer = vectorizer
        
        if 0 < budget < 1:
            self.budget = int(budget * sum(len(x) for x in documents))
        else:
            self.budget = budget   
    
    def cost(self, x):
        return len(x)
    
    def summarize(self, r=0.3, lambd=1):
        start = time.time()
        
        N = len(self.reviews)
        sim = cosine_similarity(self.vectorizer.transform(self.reviews))
        C = {i : self.cost(review) for i, review in enumerate(self.reviews)}
        V, G, U = list(range(N)), set({}), list(range(N))

        def f(S):
            cut = sum(sim[i,j] for i in (set(V)-set(S)) for j in set(S))
            redundancy = sum([sum([sim[i,j] for i in (set(S)-set({j}))]) for j in set(S)])
            return cut - lambd*redundancy

        def gain(item, f, G, C, r):
            return (f(G.union({item})) - f(G))/C[item]**r

        heap = [(-gain(u, f, G, C, r), u) for u in U]
        heapq.heapify(heap)
        while U:
            k = None        
            while k is None:
                prev_gain, head = heapq.heappop(heap)
                head_gain = -gain(head,f,G,C,r)
                if len(heap) == 0 or head_gain <= heapq.nsmallest(1,heap)[0][0]:
                    k = head
                else:
                    heapq.heappush(heap, (head_gain, head))
            if sum([C[i] for i in G]) + C[k] <= self.budget and gain(k, f, G, C, r) >= 0:
                G = G.union({k})
            U.remove(k)
        v_star = sorted([v for v in V if C[v] <= self.budget], key=lambda v: f({v}))[-1]
        if f({v_star}) >= f(G):
            G = {v_star}
            
        print('took {:.1f}s.'.format(time.time() - start))
        return [self.reviews[g] for g in G]