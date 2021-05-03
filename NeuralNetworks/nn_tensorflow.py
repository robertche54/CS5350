# Tensorflow 1.15 is required since 2.0 does not have contrib libraries
import numpy as np
import tensorflow as tf

def main(argv):
    training_set = tf.contrib.learn.datasets.base.load_csv_without_header(
      filename=argv[1],
      target_dtype=np.int,
      features_dtype=np.float32)

    test_set = tf.contrib.learn.datasets.base.load_csv_without_header(
      filename=argv[2],
      target_dtype=np.int,
      features_dtype=np.float32)

    feature_columns = [tf.contrib.layers.real_valued_column("", dimension=4)]
    classifier = tf.contrib.learn.DNNClassifier(feature_columns=feature_columns,
                    hidden_units=[argv[4]]*argv[3], n_classes=argv[3],
                    optimizer=tf.train.AdamOptimizer(learning_rate=0.001),
                    activation_fn=argv[5])
    classifier.fit(x=training_set.data, y=training_set.target, steps = 100)

    accuracy_score = classifier.evaluate(x=test_set.data, y=test_set.target)["accuracy"]
    # train_acc = classifier.evaluate(x=training_set.data, y=training_set.target)["accuracy"]
    # return str(train_acc) + " & " + str(accuracy_score)
    print(accuracy_score)
    pass

if __name__ == "__main__":
    # to_print = []
    # for i in [3, 5, 9]:
    #    for j in [5, 10, 25, 50, 100]:
    #        argv = ["nn_tensorflow.py","NeuralNetworks/train.csv","NeuralNetworks/test.csv", i, j, "relu"]
    #        to_print.append(str(i) + " & " + str(j) + " & " + str(main(argv)) + " \\\\ \\hline")
    #        pass
    #    pass
    #for s in to_print:
    #    print(s)
    argv = ["nn_tensorflow.py","NeuralNetworks/train.csv","NeuralNetworks/test.csv", 3, 5, "relu"]
    main(argv)
    pass