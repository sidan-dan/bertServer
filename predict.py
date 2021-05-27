from keras.models import load_model
# import keras
from bert_serving.client import BertClient

from nlp_classify import Self_Attention

if __name__ =='__main__':
    # predict = argmax(pred, axis=1)  # axis = 1是取行的最大值的索引，0是列的最大值的索引
    # print(predict)
    # for i in len(predict):
    #     if (predict[i] == 0) predict[i]="负"
    #     if (predict[i] == 1) predict[i]="正"
# def predict:
    print('11')

    bc = BertClient()
    m=bc.encode(['龙猫小组真棒', '关注有惊喜', '哈哈'])
    # vector_text=111
    print(m)
    model = load_model('abilstm_classify.h5',custom_objects={'Self_Attention': Self_Attention})
    pred=model.predict(m) #将测试文本向量送入模型，进行预测