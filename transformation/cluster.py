#!/usr/bin/env python3

from argparse import ArgumentParser
import sqlite3
from pathlib import Path
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.manifold import TSNE, Isomap
from sklearn.cluster import KMeans, DBSCAN
import operator
import math
import numpy as np


def pca(feature_vectors):
    return PCA(n_components=2).fit_transform(feature_vectors)


def tsne(feature_vectors):
    return TSNE(n_components=2).fit_transform(feature_vectors)


def tsvd(feature_vectors):
    return TruncatedSVD(n_components=2).fit_transform(feature_vectors)


def isomap(feature_vectors):
    return Isomap(n_components=2).fit_transform(feature_vectors)


dim_reduction_method = {
    "pca": pca,
    "tsne": tsne,
    "tsvd": tsvd,
    "isomap": isomap
}


def kmeans(coords):
    return KMeans().fit_predict(coords)


def dbscan(coords):
    return DBSCAN(eps=0.1).fit_predict(coords)


cluster_method = {
    "kmeans": kmeans,
    "dbscan": dbscan
}


def main():
    parser = ArgumentParser()
    parser.add_argument("db_path", type=Path)
    parser.add_argument("out_path", type=Path)
    parser.add_argument("--dimred", "-r", default="pca",
                        choices=dim_reduction_method.keys(),
                        help="Dimensionality reduction method to use")
    parser.add_argument("--cluster", "-c", default="kmeans",
                        choices=cluster_method.keys(),
                        help="Clustering method to use")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db_path)

    print("Creating feature vectors...")

    all_tags = conn.execute("SELECT name FROM tag").fetchall()
    all_tags = {name[0]: i for i, name in enumerate(all_tags)}

    id_and_tags = conn.execute("""SELECT seal.id, group_concat(name, ";")
            FROM seal
            JOIN seal_has_tag ON seal.id = seal_has_tag.seal_id
            JOIN tag ON tag.id = seal_has_tag.tag_id
            GROUP BY seal.id""").fetchall()
    # tags_by_seal = [{"id": id,
    #                  "tag_names": tags.split(";"),
    #                  "tags": [1 if tag in tags else 0 for tag in all_tags]}
    #                 for id, tags in tags_by_seal]
    ids = [id for id, _ in id_and_tags]
    tags = [tag_string.split(";") for _, tag_string in id_and_tags]
    feature_vectors = [[int(tag in tags_by_seal) for tag in all_tags] for tags_by_seal in tags]

    # feature_vectors = [seal["tags"] for seal in tags_by_seal]
    # # for thing in tags_by_seal:
    # #     print(thing)

    print("Reducing dimensions...")

    coords = dim_reduction_method[args.dimred](feature_vectors)

    print("Clustering coordinates...")

    clustered = cluster_method[args.cluster](coords)

    # cluster_counts = {}
    # for cluster, tags in zip(clustered, tags_by_seal):
    #     if cluster not in cluster_counts:
    #         cluster_counts[cluster] = {}
    #     for tag in tags["tag_names"]:
    #         if tag not in cluster_counts[cluster]:
    #             cluster_counts[cluster][tag] = 1
    #         else:
    #             cluster_counts[cluster][tag] += 1

    # with open(args.out_path.parent.joinpath("cluster_" + args.out_path.name), "w") as cluster_file:
    #     cluster_file.write("cluster,desc\n")
    #     for cluster, counts in cluster_counts.items():
    #         # print(cluster, "\n".join(list(map(operator.itemgetter(0), sorted(counts.items(), key=operator.itemgetter(1))[-5:]))))
    #         desc = ".".join(list(map(operator.itemgetter(0), sorted(counts.items(), key=operator.itemgetter(1))[-5:])))
    #         cluster_file.write("%i,%s\n" % (cluster, desc))

    cluster_groups = {cluster: [] for cluster in set(clustered)}
    for cluster, coord in zip(clustered, coords):
        cluster_groups[cluster].append(coord)

    cluster_extents = dict()
    # for cluster, coords in cluster_groups.items():
    #     min_coords = [math.inf, math.inf]
    #     max_coords = [-math.inf, -math.inf]
    #     for coord in coords:
    #         min_coords = np.minimum(min_coords, coord)
    #         max_coords = np.maximum(max_coords, coord)
    #     cluster_extents[cluster] = (min_coords, max_coords)

    print("Writing results...")
    with open(args.out_path, "w") as out_file:
        out_file.write("id,cluster,x,y\n")
        for coord, cluster, seal_id in zip(coords, clustered, ids):
            out_file.write("%i,%i,%f,%f\n" %
                           (seal_id, cluster, coord[0], coord[1]))

    with open(args.out_path.parent.joinpath("cluster_" + args.out_path.name), "w") as cluster_file:
        cluster_file.write("cluster,min_x,min_y,max_x,max_y\n")
        for cluster, (min_coord, max_coord) in cluster_extents.items():
            cluster_file.write("%i,%f,%f,%f,%f\n" % (cluster, *min_coord, *max_coord))


if __name__ == "__main__":
    main()
