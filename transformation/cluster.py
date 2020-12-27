#!/usr/bin/env python3

from argparse import ArgumentParser
import sqlite3
from pathlib import Path
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.manifold import TSNE, Isomap
from sklearn.cluster import KMeans, DBSCAN


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

    tags_by_seal = conn.execute("""SELECT seal.id, group_concat(name, ";")
            FROM seal
            JOIN seal_has_tag ON seal.id = seal_has_tag.seal_id
            JOIN tag ON tag.id = seal_has_tag.tag_id
            GROUP BY seal.id""").fetchall()
    tags_by_seal = [{"id": id,
                     "tags": [1 if tag in tags else 0 for tag in all_tags]}
                    for id, tags in tags_by_seal]

    feature_vectors = [seal["tags"] for seal in tags_by_seal]
    # for thing in tags_by_seal:
    #     print(thing)

    print("Reducing dimensions...")

    coords = dim_reduction_method[args.dimred](feature_vectors)

    print("Clustering coordinates...")

    clustered = cluster_method[args.cluster](coords)

    print("Writing results...")
    with open(args.out_path, "w") as out_file:
        out_file.write("id,cluster,x,y\n")
        for coord, cluster, tbs in zip(coords, clustered, tags_by_seal):
            out_file.write("%i,%i,%f,%f\n" %
                           (tbs["id"], cluster, coord[0], coord[1]))


if __name__ == "__main__":
    main()
