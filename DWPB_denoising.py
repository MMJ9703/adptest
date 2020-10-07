import pywt
import numpy as np
import pandas as pd

class DWPB():
    def __init__(self,Wavelet_basis,Max_layers):
        self.Wavelet_basis = Wavelet_basis
        self.Max_layers = Max_layers

    def _do_DWPT(self,data):#小波包分解
        wp = pywt.WaveletPacket(data, self.Wavelet_basis, maxlevel = self.Max_layers)
        Cnodes = wp.get_level(self.Max_layers, order="natural")
        Clabels = ([n.path for n in Cnodes])
        Cvalues = np.array([n.data for n in Cnodes], 'd')
        return wp,Cnodes,Clabels,Cvalues

    def _calculate_v(self,x):#提取第一层小波包系数
        v = np.array([n.data for n in x.get_level(1, order = "natural")],'d')
        return v

    def _get_median(self,x):#中值函数
        x_ = sorted(x)
        size = len(x_)
        if size % 2 == 0:
            median = (x_[size//2]+x_[size//2-1])/2
            x_[0] = median
        if size % 2 == 1:
            median = x_[(size-1)//2]
            x_[0] = median
        return x_[0]

    def _set_uthresh(self,X,sigma): #贝叶斯阈值函数
        sigmay2 = np.var(X)
        sigmax = np.sqrt(np.maximum(sigmay2-sigma**2,0))
        if sigmax == 0:
            uthresh = sorted(np.abs(X))[-1]
        else:
            uthresh = sigma**2/sigmax
        return uthresh

    def _reconstruct_coeffs(self,v,cvalues):#系数重构
        v_ = np.concatenate((v[0], v[1]))
        sigma = self._get_median(np.abs(v_)) / 0.6745
        d = pywt.WaveletPacket(None, self.Wavelet_basis, maxlevel= self.Max_layers)
        d['aaa'] = cvalues[0]
        d['aad'] = pywt.threshold(cvalues[1], self._set_uthresh(cvalues[1], sigma), 'soft')
        d['ada'] = pywt.threshold(cvalues[2], self._set_uthresh(cvalues[2], sigma), 'soft')
        d['add'] = pywt.threshold(cvalues[3], self._set_uthresh(cvalues[3], sigma), 'soft')
        d['daa'] = pywt.threshold(cvalues[4], self._set_uthresh(cvalues[4], sigma), 'soft')
        d['dad'] = pywt.threshold(cvalues[5], self._set_uthresh(cvalues[5], sigma), 'soft')
        d['dda'] = pywt.threshold(cvalues[6], self._set_uthresh(cvalues[6], sigma), 'soft')
        d['ddd'] = pywt.threshold(cvalues[7], self._set_uthresh(cvalues[7], sigma), 'soft')
        d.reconstruct(update=True)
        return d

    def denoising_process(self,df):
        time = pd.DatetimeIndex(df.index)
        inputVars = df.columns.values

        wd = []
        for var in inputVars:
            data = df[var]
            cwp, cnode, clabel, cvalue = self._do_DWPT(data)
            calv = self._calculate_v(cwp)
            d = self._reconstruct_coeffs(calv, cvalue)
            wd.append(d.data)

        wd = pd.DataFrame(wd)
        wd = wd.transpose().iloc[wd.shape[1] - len(time):, :]
        wd.index = time
        wd.columns = [inputVars]
        return wd