#########################
# "BEGINNER" quickstart #
#########################

# import tensorflow as tf

# mnist = tf.keras.datasets.mnist
# (x_train, y_train), (x_test, y_test) = mnist.load_data()
# print(x_train[0].shape)
# # MNIST returns 28 x 28 tuples

# print(type(x_train))

# # normalizing the images to 0->1
# x_train, x_test = x_train / 255.0, x_test / 255.0
# print(x_train[0])

# model = tf.keras.models.Sequential([
# 	tf.keras.layers.Flatten(input_shape=(28,28)), # input = 28,28
# 	tf.keras.layers.Dense(128, activation='relu'), # one hidden layer, 128 neurons
# 	tf.keras.layers.Dropout(0.2),
# 	tf.keras.layers.Dense(10) # creates a prediction of 10 different possibilities
# 	])

# predictions = model(x_train[:1]).numpy()
# print(predictions)
# print(tf.nn.softmax(predictions).numpy()) # use softmax to create "predictions" from 0-1

# loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True) # logits = before applying softmax.
# print(loss_fn(y_train[:1],predictions).numpy())

# model.compile(optimizer='adam',
#               loss=loss_fn,
#               metrics=['accuracy'])

# print(y_train)
# exit()
# model.fit(x_train,y_train, epochs=5)
# model.evaluate(x_test,y_test, verbose=2)

#########################
# "ADVANCED" quickstart #
#########################

import tensorflow as tf

mnist = tf.keras.datasets.mnist
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0

print(x_train.shape)
print("Adding a channels dimensions...")
x_train = x_train[...,tf.newaxis]
x_test = x_test[...,tf.newaxis]
print(x_train.shape)

print("Batching + shuffling train dataset, and batching the labels accordingly")
train_ds = tf.data.Dataset.from_tensor_slices((x_train,y_train)).shuffle(10000).batch(32)
test_ds = tf.data.Dataset.from_tensor_slices((x_test,y_test)).batch(32)

print("Creating a tensorflow model using API tf.keras.Model: this approach is similar to what is familiar in PyTorch")

class MnistModel(tf.keras.Model):
	def __init__(self):
		super(MnistModel, self).__init__()
		self.conv1 = tf.keras.layers.Conv2D(32, 3, activation='relu')
		self.flatten = tf.keras.layers.Flatten()
		self.d1 = tf.keras.layers.Dense(128, activation='relu')
		self.d2 = tf.keras.layers.Dense(10)
	
	def call(self, x):
		x = self.conv1(x)
		x = self.flatten(x)
		x = self.d1(x)
		return self.d2(x)
model = MnistModel()

loss_object = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
optimizer = tf.keras.optimizers.Adam()

# defining training and test loss, as well as accuracy.
train_loss = tf.keras.metrics.Mean(name='train_loss')
train_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name='train_accuracy')

test_loss = tf.keras.metrics.Mean(name='test_loss')
test_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name='test_accuracy')

@tf.function
def train_step(images, labels):
  with tf.GradientTape() as tape:
    # training=True is only needed if there are layers with different
    # behavior during training versus inference (e.g. Dropout).
    predictions = model(images, training=True)
    loss = loss_object(labels, predictions)
  gradients = tape.gradient(loss, model.trainable_variables)
  optimizer.apply_gradients(zip(gradients, model.trainable_variables))

  train_loss(loss)
  train_accuracy(labels, predictions)

@tf.function
def test_step(images, labels):
  # training=False is only needed if there are layers with different
  # behavior during training versus inference (e.g. Dropout).
  predictions = model(images, training=False)
  t_loss = loss_object(labels, predictions)

  test_loss(t_loss)
  test_accuracy(labels, predictions)

EPOCHS = 5

for epoch in range(EPOCHS):
  # Reset the metrics at the start of the next epoch
  train_loss.reset_states()
  train_accuracy.reset_states()
  test_loss.reset_states()
  test_accuracy.reset_states()

  for images, labels in train_ds:
    train_step(images, labels)

  for test_images, test_labels in test_ds:
    test_step(test_images, test_labels)

  template = 'Epoch {}, Loss: {}, Accuracy: {}, Test Loss: {}, Test Accuracy: {}'
  print(template.format(epoch + 1,
                        train_loss.result(),
                        train_accuracy.result() * 100,
                        test_loss.result(),
                        test_accuracy.result() * 100))
