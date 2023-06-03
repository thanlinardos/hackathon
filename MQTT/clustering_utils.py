from sklearn.cluster import KMeans
import math
import matplotlib.pyplot as plt
import numpy as np

def check_cluster_multitudes(test_cases,edge_point_list):
    wcss = []
    for i in test_cases:
        kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=120, n_init=5, random_state=0)  #increase max_iter and n_init for more accurate error results for elbow graph and elbow finding, decrease for faster 'find errors for test cases' time
        kmeans.fit(edge_point_list)
        wcss.append(kmeans.inertia_)
    return wcss

def plot_cluster_graph(test_cases, wcss):
    plt.plot(test_cases, wcss)
    plt.title('Elbow Method')
    plt.xlabel('Number of clusters')
    plt.ylabel('WCSS')
    plt.show()
    

def find_elbow(wcss,test_cases):
    #basically get wcss, derive once, make abs(),derive again, make abs,find index of maximum, add 1 and you get the elbow index
    diffs=list(map(abs,np.diff(wcss)))
    diffs_log=list(map(math.log,diffs))
    diffs_of_diffs=list(map(abs,np.diff(diffs_log)))
    n=test_cases[diffs_of_diffs.index(max(diffs_of_diffs))+1]  #basically +2 cuse of double derivation and -1 because of list index starting from 0
    # plot_cluster_graph(test_cases[:-2],diffs_of_diffs)

    print('guessing ',n,' bus lines')
    return n

def find_centers(edge_point_list,n):
    kmeans = KMeans(n_clusters=n, init='k-means++', max_iter=150, n_init=8, random_state=0)
    kmeans.fit(edge_point_list)
    # print(kmeans.cluster_centers_)

    centers=kmeans.cluster_centers_[:,0]
    labels=kmeans.labels_
    # for i in range(len(labels)):
    #     print(labels[i])
    #     print(edge_point_list[i])
    return centers,labels
