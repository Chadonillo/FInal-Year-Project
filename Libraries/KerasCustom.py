import tensorflow.keras.backend as K
import tensorflow as tf

def winMetric(acc_dir_train, acc_dir_test, threshold=0.6):
    m = tf.keras.metrics.Accuracy()
    # Create a loss function that adds the MSE loss to the mean of all squared activations of a specific layer
    def winRatio(y_true,y_pred):
        class_id_preds = K.argmax(y_pred, axis=-1)
        class_id_scores = K.max(y_pred, axis=-1, keepdims=False)
        
        allPredTrades_Pos = K.cast(K.not_equal(class_id_preds, 2), 'bool') #[0,0,0,1,0,1,0,1,1]
        trades_predicted = tf.boolean_mask(class_id_preds, allPredTrades_Pos)
        trades_acc_dir = tf.boolean_mask(acc_dir_train, allPredTrades_Pos)
        trades_scores = tf.boolean_mask(class_id_scores, allPredTrades_Pos)
        
        allAccTrades_Pos = K.cast(K.not_equal(trades_acc_dir, 2), 'bool') #[0,0,0,1,0,1,0,1,1]
        trades_predicted = tf.boolean_mask(trades_predicted, allAccTrades_Pos)
        trades_acc_dir = tf.boolean_mask(trades_acc_dir, allAccTrades_Pos)
        trades_scores = tf.boolean_mask(trades_scores, allAccTrades_Pos)

        filtering_mask = trades_scores >= threshold
        trades_predicted = tf.boolean_mask(trades_predicted, filtering_mask)
        trades_acc_dir = tf.boolean_mask(trades_acc_dir, filtering_mask)

        m.update_state(trades_predicted, trades_acc_dir)
        return m.result()
   
    # Return a function
    return winRatio

def TradeFrequency(acc_dir_train, acc_dir_test, threshold=0.6):
    # Create a loss function that adds the MSE loss to the mean of all squared activations of a specific layer
    def NoTradesInBatch(y_true,y_pred):
        class_id_preds = K.argmax(y_pred, axis=-1)
        class_id_scores = K.max(y_pred, axis=-1, keepdims=False)
        
        allPredTrades_Pos = K.cast(K.not_equal(class_id_preds, 2), 'bool') #[0,0,0,1,0,1,0,1,1]
        trades_predicted = tf.boolean_mask(class_id_preds, allPredTrades_Pos)
        trades_acc_dir = tf.boolean_mask(acc_dir_train, allPredTrades_Pos)
        trades_scores = tf.boolean_mask(class_id_scores, allPredTrades_Pos)
        
        allAccTrades_Pos = K.cast(K.not_equal(trades_acc_dir, 2), 'bool') #[0,0,0,1,0,1,0,1,1]
        trades_predicted = tf.boolean_mask(trades_predicted, allAccTrades_Pos)
        trades_acc_dir = tf.boolean_mask(trades_acc_dir, allAccTrades_Pos)
        trades_scores = tf.boolean_mask(trades_scores, allAccTrades_Pos)

        filtering_mask = trades_scores >= threshold
        trades_predicted = tf.boolean_mask(trades_predicted, filtering_mask)
        trades_acc_dir = tf.boolean_mask(trades_acc_dir, filtering_mask)
        
        if tf.size(trades_predicted)==None:
            return 0
        return tf.size(trades_predicted)
   
    # Return a function
    return NoTradesInBatch