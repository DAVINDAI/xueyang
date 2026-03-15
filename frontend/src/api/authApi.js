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
  if (response.data.accessToken) {
    localStorage.setItem('token', response.data.accessToken);
    // 登录成功后清除访客ID
    localStorage.removeItem('visitorId');
  }
  return response.data;
};

/**
 * 注销
 */
export const logout = () => {
  localStorage.removeItem('token');
  // 登出后重新生成访客ID
  localStorage.removeItem('visitorId');
  // 生成新的访客ID
  const generateVisitorId = () => {
    return 'visitor_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
  };
  localStorage.setItem('visitorId', generateVisitorId());
};

/**
 * 获取当前登录状态
 * @returns {boolean}
 */
export const isLoggedIn = () => {
  return !!localStorage.getItem('token');
};
