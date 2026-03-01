import axios from './index';

/**
 * 发送验证码
 * @param {string} phone - 手机号
 * @returns {Promise}
 */
export const sendVerificationCode = async (phone) => {
  const response = await axios.post('/auth/send-code', { phone });
  return response.data;
};

/**
 * 登录
 * @param {string} phone - 手机号
 * @param {string} code - 验证码
 * @returns {Promise}
 */
export const login = async (phone, code) => {
  const response = await axios.post('/auth/login', { phone, code });
  // 存储token到localStorage
  if (response.accessToken) {
    localStorage.setItem('token', response.accessToken);
  }
  return response;
};

/**
 * 注销
 */
export const logout = () => {
  localStorage.removeItem('token');
};

/**
 * 获取当前登录状态
 * @returns {boolean}
 */
export const isLoggedIn = () => {
  return !!localStorage.getItem('token');
};
