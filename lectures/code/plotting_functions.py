import matplotlib.pyplot as plt
import mglearn
import numpy as np
from imageio import imread
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.model_selection import cross_validate
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC

from utils import tree_image
from mglearn_utils import *

def plot_tree_decision_boundary(
    model, X, y, x_label="x-axis", y_label="y-axis", eps=None, ax=None, title=None
):
    if ax is None:
        ax = plt.gca()

    if title is None:
        title = "max_depth=%d" % (model.tree_.max_depth)

    
    plot_2d_separator(model, X.to_numpy(), eps=eps, fill=True, alpha=0.5, ax=ax)
    discrete_scatter(X.iloc[:, 0], X.iloc[:, 1], y, ax=ax)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)


def plot_tree_decision_boundary_and_tree(
    model, X, y, height=6, width=16, x_label="x-axis", y_label="y-axis", eps=None
):
    fig, ax = plt.subplots(
        1,
        2,
        figsize=(width, height),
        subplot_kw={"xticks": (), "yticks": ()},
        gridspec_kw={"width_ratios": [1.5, 2]},
    )
    plot_tree_decision_boundary(model, X, y, x_label, y_label, eps, ax=ax[0])
    ax[1].imshow(tree_image(X.columns, model))
    ax[1].set_axis_off()
    plt.show()


def plot_fruit_tree(ax=None):
    import graphviz

    if ax is None:
        ax = plt.gca()
    mygraph = graphviz.Digraph(
        node_attr={"shape": "box"}, edge_attr={"labeldistance": "10.5"}, format="png"
    )
    mygraph.node("0", "Is tropical?")
    mygraph.node("1", "Has pit?")
    mygraph.node("2", "Is red?")
    mygraph.node("3", "Mango")
    mygraph.node("4", "Banana")
    mygraph.node("5", "Cherry")
    mygraph.node("6", "Kiwi")
    mygraph.edge("0", "1", label="True")
    mygraph.edge("0", "2", label="False")
    mygraph.edge("1", "3", label="True")
    mygraph.edge("1", "4", label="False")
    mygraph.edge("2", "5", label="True")
    mygraph.edge("2", "6", label="False")
    mygraph.render("tmp")
    ax.imshow(imread("tmp.png"))
    ax.set_axis_off()


def plot_knn_clf(
    X_train, y_train, X_test, n_neighbors=1, class_names=("class 0", "class 1"), test_format="star"
):
    # credit: This function is based on: https://github.com/amueller/mglearn/blob/master/mglearn/plot_knn_classification.py
    plt.clf()
    print("n_neighbors", n_neighbors)
    dist = euclidean_distances(X_train, X_test)
    closest = np.argsort(dist, axis=0)
    clf = KNeighborsClassifier(n_neighbors=n_neighbors).fit(X_train, y_train)
    plot_train_test_points(X_train, y_train, X_test, list(class_names), test_format)
    for x, neighbors in zip(X_test, closest.T):
        for neighbor in neighbors[:n_neighbors]:
            plt.arrow(
                x[0],
                x[1],
                X_train[neighbor, 0] - x[0],
                X_train[neighbor, 1] - x[1],
                head_width=0,
                fc="k",
                ec="k",
            )
    plt.show()


def plot_knn_decision_boundaries(X_train, y_train, k_values=(1, 11, 100)):
    fig, axes = plt.subplots(1, len(k_values), figsize=(15, 4))

    for n_neighbors, ax in zip(k_values, axes):
        clf = KNeighborsClassifier(n_neighbors=n_neighbors)
        scores = cross_validate(clf, X_train, y_train, return_train_score=True)
        mean_valid_score = scores["test_score"].mean()
        mean_train_score = scores["train_score"].mean()
        clf.fit(X_train, y_train)
        mglearn.plots.plot_2d_separator(
            clf, X_train.to_numpy(), fill=True, eps=0.5, ax=ax, alpha=0.4
        )
        mglearn.discrete_scatter(X_train.iloc[:, 0], X_train.iloc[:, 1], y_train, ax=ax)
        title = "n_neighbors={}\n train score={}, valid score={}".format(
            n_neighbors, round(mean_train_score, 2), round(mean_valid_score, 2)
        )
        ax.set_title(title)
        ax.set_xlabel("longitude")
        ax.set_ylabel("latitude")
    axes[0].legend(loc=1)


def plot_train_test_points(
    X_train, y_train, X_test, class_names=("class 0", "class 1"), test_format="star"
):
    training_points = mglearn.discrete_scatter(X_train[:, 0], X_train[:, 1], y_train)
    if test_format == "circle":
        test_points = mglearn.discrete_scatter(X_test[:, 0], X_test[:, 1], markers="o", c="k", s=18)
    else:
        test_points = mglearn.discrete_scatter(X_test[:, 0], X_test[:, 1], markers="*", c="g", s=16)
    plt.legend(
        training_points + test_points,
        [class_names[0], class_names[1], "test point(s)"],
    )


def plot_support_vectors(svm, X, y):
    mglearn.plots.plot_2d_separator(svm, X, eps=0.5)
    mglearn.discrete_scatter(X[:, 0], X[:, 1], y)
    sv = svm.support_vectors_  # plot support vectors
    # class labels of support vectors are given by the sign of the dual coefficients
    sv_labels = svm.dual_coef_.ravel() > 0
    mglearn.discrete_scatter(sv[:, 0], sv[:, 1], sv_labels, s=15, markeredgewidth=3)
    plt.xlabel("Feature 0")
    plt.ylabel("Feature 1")


def plot_svc_gamma(param_grid, X_train, y_train, x_label="longitude", y_label="latitude"):
    fig, axes = plt.subplots(1, len(param_grid), figsize=(len(param_grid) * 5, 4))
    for gamma, ax in zip(param_grid, axes):
        clf = SVC(gamma=gamma)
        scores = cross_validate(clf, X_train, y_train, return_train_score=True)
        mean_valid_score = scores["test_score"].mean()
        mean_train_score = scores["train_score"].mean()
        clf.fit(X_train, y_train)
        mglearn.plots.plot_2d_separator(clf, X_train, fill=True, eps=0.5, ax=ax, alpha=0.4)
        mglearn.discrete_scatter(X_train[:, 0], X_train[:, 1], y_train, ax=ax)
        title = "gamma={}\n train score={}, valid score={}".format(
            gamma, round(mean_train_score, 2), round(mean_valid_score, 2)
        )
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
    axes[0].legend(loc=1)


def plot_svc_C(param_grid, X_train, y_train, x_label="longitude", y_label="latitude"):
    fig, axes = plt.subplots(1, len(param_grid), figsize=(len(param_grid) * 5, 4))
    for C, ax in zip(param_grid, axes):
        clf = SVC(C=C, gamma=0.01)
        scores = cross_validate(clf, X_train, y_train, return_train_score=True)
        mean_valid_score = scores["test_score"].mean()
        mean_train_score = scores["train_score"].mean()
        clf.fit(X_train, y_train)
        mglearn.plots.plot_2d_separator(clf, X_train, fill=True, eps=0.5, ax=ax, alpha=0.4)
        mglearn.discrete_scatter(X_train[:, 0], X_train[:, 1], y_train, ax=ax)
        title = "C={}\n train score={}, valid score={}".format(
            C, round(mean_train_score, 2), round(mean_valid_score, 2)
        )
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
    axes[0].legend(loc=1)


def make_bracket(s, xy, textxy, width, ax):
    annotation = ax.annotate(
        s,
        xy,
        textxy,
        ha="center",
        va="center",
        size=20,
        arrowprops=dict(
            arrowstyle="-[",
            fc="w",
            ec="k",
            lw=2,
        ),
        bbox=dict(boxstyle="square", fc="w"),
    )
    annotation.arrow_patch.get_arrowstyle().widthB = width


def plot_improper_processing(estimator_name):
    # Adapted from https://github.com/amueller/mglearn/blob/106cf48ef03710ef1402813997746741aa6467da/mglearn/plot_improper_preprocessing.py#L12
    fig, axes = plt.subplots(2, 1, figsize=(15, 10))

    for axis in axes:
        bars = axis.barh(
            [0, 0, 0],
            [11.9, 2.9, 4.9],
            left=[0, 12, 15],
            color=["white", "grey", "grey"],
            hatch="//",
            align="edge",
            edgecolor="k",
        )
        bars[2].set_hatch(r"")
        axis.set_yticks(())
        axis.set_frame_on(False)
        axis.set_ylim(-0.1, 6)
        axis.set_xlim(-0.1, 20.1)
        axis.set_xticks(())
        axis.tick_params(length=0, labeltop=True, labelbottom=False)
        axis.text(
            6, -0.3, "training folds", fontdict={"fontsize": 14}, horizontalalignment="center"
        )
        axis.text(
            13.5, -0.3, "validation fold", fontdict={"fontsize": 14}, horizontalalignment="center"
        )
        axis.text(17.5, -0.3, "test set", fontdict={"fontsize": 14}, horizontalalignment="center")

    make_bracket("scaler fit", (7.5, 1.3), (7.5, 2.0), 15, axes[0])
    make_bracket(estimator_name + " fit", (6, 3), (6, 4), 12, axes[0])
    make_bracket(estimator_name + "predict", (13.4, 3), (13.4, 4), 2.5, axes[0])

    axes[0].set_title("Cross validation")
    axes[1].set_title("Test set prediction")

    make_bracket("scaler fit", (7.5, 1.3), (7.5, 2.0), 15, axes[1])
    make_bracket(estimator_name + " fit", (7.5, 3), (7.5, 4), 15, axes[1])
    make_bracket(estimator_name + " predict", (17.5, 3), (17.5, 4), 4.8, axes[1])


def plot_proper_processing(estimator_name):
    # Adapted from https://github.com/amueller/mglearn/blob/106cf48ef03710ef1402813997746741aa6467da/mglearn/plot_improper_preprocessing.py#L12

    fig, axes = plt.subplots(2, 1, figsize=(15, 8))

    for axis in axes:
        bars = axis.barh(
            [0, 0, 0],
            [11.9, 2.9, 4.9],
            left=[0, 12, 15],
            color=["white", "grey", "grey"],
            hatch="//",
            align="edge",
            edgecolor="k",
        )
        bars[2].set_hatch(r"")
        axis.set_yticks(())
        axis.set_frame_on(False)
        axis.set_ylim(-0.1, 4.5)
        axis.set_xlim(-0.1, 20.1)
        axis.set_xticks(())
        axis.tick_params(length=0, labeltop=True, labelbottom=False)
        axis.text(
            6, -0.3, "training folds", fontdict={"fontsize": 14}, horizontalalignment="center"
        )
        axis.text(
            13.5, -0.3, "validation fold", fontdict={"fontsize": 14}, horizontalalignment="center"
        )
        axis.text(17.5, -0.3, "test set", fontdict={"fontsize": 14}, horizontalalignment="center")

    make_bracket("scaler fit", (6, 1.3), (6, 2.0), 12, axes[0])
    make_bracket(estimator_name + " fit", (6, 3), (6, 4), 12, axes[0])
    make_bracket(estimator_name + " predict", (13.4, 3), (13.4, 4), 2.5, axes[0])

    axes[0].set_title("Cross validation")
    axes[1].set_title("Test set prediction")

    make_bracket("scaler fit", (7.5, 1.3), (7.5, 2.0), 15, axes[1])
    make_bracket(estimator_name + " fit", (7.5, 3), (7.5, 4), 15, axes[1])
    make_bracket(estimator_name + " predict", (17.5, 3), (17.5, 4), 4.8, axes[1])
    fig.subplots_adjust(hspace=0.3)


def plot_original_scaled(
    X_train,
    X_test,
    train_transformed,
    test_transformed,
    title_transformed="Properly transformed",
):
    fig, axes = plt.subplots(1, 2, figsize=(15, 4))
    axes[0].scatter(X_train[:, 0], X_train[:, 1], label="Training set", s=60)
    axes[0].scatter(
        X_test[:, 0],
        X_test[:, 1],
        marker="^",
        color=mglearn.cm2(1),
        label="Test set",
        s=60,
    )
    axes[0].legend(loc="upper right")

    axes[0].set_title("Original Data")

    axes[1].scatter(train_transformed[:, 0], train_transformed[:, 1], label="Training set", s=60)
    axes[1].scatter(
        test_transformed[:, 0],
        test_transformed[:, 1],
        marker="^",
        color=mglearn.cm2(1),
        label="Test set",
        s=60,
    )
    axes[1].legend(loc="upper right")
    axes[1].set_title(title_transformed)


def plot_logistic_regression(x, w):
    import graphviz

    sentiment = "pos" if sum(w) > 0 else "neg"
    lr_graph = graphviz.Digraph(
        node_attr={"shape": "circle", "fixedsize": "False"},
        graph_attr={"rankdir": "LR", "splines": "line"},
    )
    inputs = graphviz.Digraph(node_attr={"shape": "circle"}, name="cluster_0")
    output = graphviz.Digraph(node_attr={"shape": "circle"}, name="cluster_2")

    for i in range(len(x)):
        inputs.node(x[i], labelloc="c")
    inputs.body.append('label = "inputs"')
    inputs.body.append('color = "white"')

    lr_graph.subgraph(inputs)

    output.body.append('label = "output"')
    output.body.append('color = "white"')
    output.node("y_hat=%s" % sentiment)

    lr_graph.subgraph(output)
    print("Weighted sum of the input features = %0.3f y_hat = %s" % (sum(w), sentiment))
    for i in range(len(w)):
        lr_graph.edge(x[i], "y_hat=%s" % sentiment, label=str(w[i]))
    return lr_graph


def plot_confusion_matrix_ex(tn, fp, fn, tp, target="Fraud"):
    plt.figure(figsize=(7, 7))
    confusion = np.array([[tn, fp], [fn, tp]])
    plt.text(0.40, 0.7, confusion[0, 0], size=45, horizontalalignment="right")
    plt.text(0.40, 0.2, confusion[1, 0], size=45, horizontalalignment="right")
    plt.text(0.90, 0.7, confusion[0, 1], size=45, horizontalalignment="right")
    plt.text(0.90, 0.2, confusion[1, 1], size=45, horizontalalignment="right")
    plt.xticks(
        [0.25, 0.75], ["predicted not " + target, "predicted " + target], size=20, rotation=25
    )
    plt.yticks([0.25, 0.75], ["true " + target, "true not " + target], size=20)
    plt.plot([0.5, 0.5], [0, 1], "--", c="k")
    plt.plot([0, 1], [0.5, 0.5], "--", c="k")

    plt.xlim(0, 1)
    plt.ylim(0, 1)


def plot_confusion_matrix_example(tn, fp, fn, tp, target="Fraud"):
    fig, ax = plt.subplots(1, 2, figsize=(20, 6), subplot_kw={"xticks": (), "yticks": ()})

    plt.setp(
        ax,
        xticks=[0.25, 0.75],
        xticklabels=["predicted not " + target, "predicted " + target],
        yticks=[0.25, 0.75],
        yticklabels=["true " + target, "true not " + target],
    )
    confusion = np.array([[tn, fp], [fn, tp]])
    ax[0].text(0.40, 0.7, confusion[0, 0], size=45, horizontalalignment="right")
    ax[0].text(0.40, 0.2, confusion[1, 0], size=45, horizontalalignment="right")
    ax[0].text(0.90, 0.7, confusion[0, 1], size=45, horizontalalignment="right")
    ax[0].text(0.90, 0.2, confusion[1, 1], size=45, horizontalalignment="right")
    ax[0].plot([0.5, 0.5], [0, 1], "--", c="k")
    ax[0].plot([0, 1], [0.5, 0.5], "--", c="k")

    ax[0].set_xlim(0, 1)
    ax[0].set_ylim(0, 1)

    ax[1].text(0.45, 0.6, "TN", size=100, horizontalalignment="right")
    ax[1].text(0.45, 0.1, "FN", size=100, horizontalalignment="right")
    ax[1].text(0.95, 0.6, "FP", size=100, horizontalalignment="right")
    ax[1].text(0.95, 0.1, "TP", size=100, horizontalalignment="right")
    ax[1].plot([0.5, 0.5], [0, 1], "--", c="k")
    ax[1].plot([0, 1], [0.5, 0.5], "--", c="k")
    ax[1].yaxis.set_tick_params(labelsize=12)
    ax[1].set_xlim(0, 1)
    ax[1].set_ylim(0, 1)


def make_num_tree_plot(
    preprocessor, X_train, y_train, X_test, y_test, num_trees, scoring_metric="accuracy"
):
    """
    Make number of trees vs error rate plot for RandomForestClassifier

    Parameters
    ----------
    X_train: numpy.ndarray
        The X part of the train set
    y_train: numpy.ndarray
        The y part of the train set
    X_test: numpy.ndarray
        The X part of the test/validation set
    y_test: numpy.ndarray
        The y part of the test/validation set
    num_trees: List[int]
        The value for `n_estimators` argument of RandomForestClassifier
    -------
        Shows the number of trees vs error rate plot

    """
    train_scores = []
    test_scores = []
    for ntree in num_trees:
        model = make_pipeline(preprocessor, RandomForestClassifier(n_estimators=ntree))
        scores = cross_validate(
            model, X_train, y_train, return_train_score=True, scoring=scoring_metric
        )
        train_scores.append(np.mean(scores["train_score"]))
        test_scores.append(np.mean(scores["test_score"]))

    plt.semilogx(num_trees, train_scores, label="train")
    plt.semilogx(num_trees, test_scores, label="cv")
    plt.legend()
    plt.xlabel("number of trees")
    plt.ylabel("scores")
