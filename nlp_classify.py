"""
该文件用于bert进行特征提取
然后利用BLSTM与Attention进行文本分类，训练模型并且保存。
"""
import pymysql
import matplotlib.pyplot as plt
from keras.utils import to_categorical
from keras.layers import Input, BatchNormalization, Dense,Bidirectional, LSTM,Dropout
from keras import Input, losses, Sequential
from keras import backend as K
from keras.layers.core import Flatten
from keras.engine.topology import Layer
from keras_layer_normalization import LayerNormalization
from sklearn.model_selection import train_test_split
import numpy as np
from keras.callbacks import Callback
from sklearn.metrics import f1_score, precision_score, recall_score



class Metrics(Callback):

    def __init__(self, valid_data):

        super(Metrics, self).__init__()
        self.validation_data = valid_data


    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        val_predict = np.argmax(self.model.predict(self.validation_data[0]), -1)
        val_targ = self.validation_data[1]
        if len(val_targ.shape) == 2 and val_targ.shape[1] != 1:
            val_targ = np.argmax(val_targ, -1)

        _val_f1 = f1_score(val_targ, val_predict, average='macro')
        _val_recall = recall_score(val_targ, val_predict, average='macro')
        _val_precision = precision_score(val_targ, val_predict, average='macro')

        logs['val_f1'] = _val_f1
        logs['val_recall'] = _val_recall
        logs['val_precision'] = _val_precision
        print(" — val_f1: %f — val_precision: %f — val_recall: %f" % (_val_f1, _val_precision, _val_recall))
        return


class Self_Attention(Layer):

    def __init__(self, output_dim, **kwargs):
        self.output_dim = output_dim
        super(Self_Attention, self).__init__(**kwargs)

    def build(self, input_shape):
        # 为该层创建一个可训练的权重
        # inputs.shape = (batch_size, time_steps, seq_len)
        self.kernel = self.add_weight(name='kernel',
                                      shape=(3, input_shape[2], self.output_dim),
                                      initializer='uniform',
                                      trainable=True)

        super(Self_Attention, self).build(input_shape)  # 一定要在最后调用它

    def call(self, x):
        WQ = K.dot(x, self.kernel[0])
        WK = K.dot(x, self.kernel[1])
        WV = K.dot(x, self.kernel[2])

        print("WQ.shape", WQ.shape)

        print("K.permute_dimensions(WK, [0, 2, 1]).shape", K.permute_dimensions(WK, [0, 2, 1]).shape)

        QK = K.batch_dot(WQ, K.permute_dimensions(WK, [0, 2, 1]))

        QK = QK / (64 ** 0.5)

        QK = K.softmax(QK)

        print("QK.shape", QK.shape)

        V = K.batch_dot(QK, WV)

        return V

    def get_config(self):  #在有自定义网络层时，需要保存模型时，重写get_config函数
        config = {"output_dim": self.output_dim}
        base_config = super(Self_Attention, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[1], self.output_dim)


max_features = 20000

class Classify():

    def load_data(self):
        # db = pymysql.connect(host="124.71.109.151", user="root", password=".Rebootcat2020.", port=3306, db="my_db",
        #                      charset="utf8")
        # db = pymysql.connect(host="localhost", user="root", password="hsk123456", port=3306, db="dianping",
        #                      charset="utf8")
        db = pymysql.connect(host="localhost", user="root", password=".Rebootcat2020.", port=3306, db="my_db",
                             charset="utf8")

        cursor = db.cursor()
        # 3编写sql
        # sql = "select id_review,shop_comment from shop_comment where id_review<5"
        sql = "select * from encode where taste >=5 and service =5 and environment=5 and id<100000 or(taste <=3 and service<=3 and environment<=3 and id<350000) "
        # 4.执行sql
        cursor.execute(sql)
        # 5.查看结果
        r_encodes = []
        score_lists = []
        results = cursor.fetchall()  # 用于返回多条数据
        for i in results:
            need = i[1].replace("[",'')
            need = need.replace("]",'')
            need_list = need.split(",")
            # print(type(need_list))
            # print(type(need_list[0]))
            need_list = [float(i) for i in need_list]
            # print(type(need_list[0]))

            info = np.array(need_list)
            taste = float(i[2])
            environment = float(i[3])
            service = float(i[4])
            if taste >= 5 and environment >= 4.5 and service >= 4.5:
                label = 1  # positive
                r_encodes.append(info)
                score_lists.append(label)
            elif taste < 3 and environment < 3 and service < 3:
                label = 0  # negative
                r_encodes.append(info)
                score_lists.append(label)
            else:
                pass

        cursor.close()
        # 关闭数据库
        db.close()
        return r_encodes,score_lists

    def train_model(self):
        review_list, score_list = self.load_data()
        x_train, x_test, y_train, y_test = train_test_split(review_list, score_list, test_size=0.2, random_state=42)
        # x_train = self.encode_data(x_train)
        # print(type(x_train))
        x_train = np.array(x_train)
        x_test = np.array(x_test)
        train_shape1 = x_train.shape
        x_train = x_train.reshape(train_shape1[0],train_shape1[1],1)
        # x_test = self.encode_data(x_test)
        x_test = x_test.reshape(x_test.shape[0],x_test.shape[1],1)
        # print(x_train.shape)
        # print(x_test.shape)

        num_classes = 2
        y_train = to_categorical(y_train, num_classes)
        y_test = to_categorical(y_test, num_classes)
        # 创建模型
        input_shape = (768, 1)
        model = Sequential()
        model.add(Bidirectional(LSTM(50, activation='tanh',return_sequences=True),input_shape=input_shape))
        # model.add(Bidirectional(LSTM(50, activation='tanh', input_shape=(768,),return_sequences=False)))

        model.add(Self_Attention(128))
        model.add(Dropout(0.3))
        model.add(LayerNormalization())

        model.add(Flatten())
        model.add(Dense(2, activation='softmax'))
        # model.compile(loss='categorical_crossentropy', optimizer=SGD(lr=0.003, momentum=0.9, nesterov=True), metrics=['accuracy'])
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        model.build(input_shape=(768,1))
        print(model.summary())


        model.compile(loss='categorical_crossentropy',
                      # optimizer=Adam(),
                      metrics=['accuracy'])

        # 模型训练以及评估
        # batch_size :每个小批量包含的样本数，eg，batch_size = 8,每次处理8个样本
        # epochs:训练的轮数，一般要训练100以上，160是可以的
        # 在所有训练数据上迭代一次叫作一个轮次（epoch）］
        # verbose = 0，在控制台没有任何输出
        # verbose = 1 ：显示进度条   默认为1
        # verbose = 2：为每个epoch输出一行记录
        # model.fit(x_train, y_train, batch_size=8, epochs=3,callbacks=[PlotLossesKeras()],verbose=0)
        History = model.fit(x_train, y_train, batch_size=64, epochs=20,validation_data=(x_test,y_test), callbacks=Metrics(valid_data=(x_test,y_test)))
        # History = model.fit(x_train, y_train, batch_size=16, epochs=12,
        #                     validation_data=(x_test,y_test), callbacks=Metrics(valid_data=(x_test,y_test)))
        with open("score_info.txt","w",encoding='utf-8') as f:
            f.write(str(History.history))
        model.save('abilstm_classify.h5')
        print('this is model_evaluate',model.evaluate(x_test, y_test))
        print("end!", "-*100")
        model.compile(optimizer='adam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        acc = History.history['accuracy']
        val_acc = History.history['val_accuracy']
        loss = History.history['loss']
        val_loss = History.history['val_loss']
        f1 = History.history['val_f1']
        recall = History.history['val_recall']
        precision = History.history['val_precision']
        epochs = range(len(acc))

        plt.plot(epochs, acc, 'skyblue', label='Training accuracy')
        plt.plot(epochs, val_acc, 'sandybrown', label='validation accuracy')
        plt.title('Training and validation accuracy')
        plt.legend(loc='upper left')
        plt.xlabel("epoch")
        plt.ylabel("acc")
        plt.savefig('acc.png')  # 保存图片

        plt.clf()   #清空图像
        plt.plot(epochs, loss, 'skyblue', label='Training loss')
        plt.plot(epochs, val_loss, 'sandybrown', label='validation loss')
        plt.title('Training and validation loss')
        plt.xlabel("epoch")
        plt.ylabel("loss")
        plt.legend(loc='upper left')
        plt.savefig('loss.png')  # 保存图片

        plt.clf()  # 清空图像
        plt.plot(epochs, f1, 'skyblue', label='F1-score')
        plt.plot(epochs, recall, 'sandybrown', label='Recall')
        plt.plot(epochs, precision, 'gray', label='Precision')
        plt.title('F1、Recall and Precision score')
        plt.xlabel("epoch")
        plt.ylabel("score")
        plt.legend(loc='upper left')
        plt.savefig('score.png')  # 保存图片

    def analyse_model(self,all_content):
        _custom_objects = {
            "Mylayer": Self_Attention,
        }
        from keras.models import load_model
        from bert_serving.client import BertClient
        bc = BertClient()
        x_train = bc.encode(all_content)
        print(x_train)
        train_shape1 = x_train.shape
        x_train = x_train.reshape(train_shape1[0], train_shape1[1], 1)
        # model =tf.keras.models.load_model("/root/python/hsk/python/nlp/abilstm_classify.h5", custom_objects=_custom_objects)
        model = load_model('abilstm_classify.h5',custom_objects={'Self_Attention': Self_Attention})  # 选取自己的.h模型名称
        print("load model successfully!")
        pred = model.predict(x_train)
        print("this is result!")
        print(pred)
        print(type(pred))
        for i in pred:
            print(len(i))
        print("-"*100)
        pred = model.predict_proba(x_train)
        print("this is result!")
        print(pred)
        return pred

    def load_model(self):
        _custom_objects = {
            "Mylayer": Self_Attention,
        }
        from keras.models import load_model
        from bert_serving.client import BertClient
        from keras.applications.resnet50 import preprocess_input, decode_predictions
        # import tensorflow as tf
        bc = BertClient()
        text = [
            '他们家的排队实在是太夸张了，来了两次这一次才排上，这次排上的主要原因是因为我提前了两个小时就开始关注排队的情况。然后排上队，再去的话其实都已经隔了将近两个小时，真的太夸张了，他们家的人也太多了。 然后呢，说一下菜吧，他们家的菜我点的是最贵的那一个锅，我觉得贵的肯定会有贵的道理，但没想到这个锅真的挺好吃，我们隔壁锅吃的是新出的那一个。我感觉整个就像一个红烧味儿非常的普通，我觉得我点的这一个济州岛这个八爪鱼，如果喜欢吃海的可以尝试一下，它是有一点点甜辣的，而且辣味会比较偏多一些，相对于四川人来说应该会更喜欢。整个锅的东西还是很丰富，有鸡翅啊，年糕，虾，米团还有一些小的东西还是不错的。 下一次的话还是打算点一下部队火锅尝一下和别家有什么不一样，他们家这个八爪鱼的锅确实是和别的韩式料理。很不一样，再说一下他们家的南瓜粥很好喝，还可以无限续。',
            '中午十二点到的，排队排了四十分钟左右！真的人很多，一上来就送了很多小菜，味道也挺好的，赞赞赞！炒年糕极力推荐！！！鸡肉锅有一点腻！小姐姐们的服务也超级好，看到我们的菜有点冷了，就马上帮我们热！！！以后还会来光顾的',
            '没有网上吹的那么好吃，性价比也没有网上说的那么高，一百多的哪个锅看起来价格很便宜，但是里面的菜品也很少',
            '味道偏中式 环境一般 排队很久 感觉不值得这个时间',
            '说实话味道真的一般 价格很便宜 排队人太多了 大多数都是大学生 反正我不会去第二次了',
            '环境真的不好，服务业差，价格也贵，就是菜量挺大，味道还行，别的真的没啥可推荐的']
        x_train = bc.encode(text)
        print(x_train)
        train_shape1 = x_train.shape
        x_train = x_train.reshape(train_shape1[0], train_shape1[1], 1)
        # model =tf.keras.models.load_model("/root/python/hsk/python/nlp/abilstm_classify.h5", custom_objects=_custom_objects)
        model = load_model('abilstm_classify.h5', custom_objects={'Self_Attention': Self_Attention})  # 选取自己的.h模型名称
        print("load model successfully!")
        pred = model.predict(x_train)
        print("this is result!")
        print(pred)
        print(type(pred))
        for i in pred:
            print(len(i))
        print("-" * 100)
        pred = model.predict_proba(x_train)
        print("this is result!")
        print(pred)


if __name__ =='__main__':
    obj = Classify()
    # r_encodes,score_lists=obj.load_data()
    # obj.train_model()
    obj.load_model()





