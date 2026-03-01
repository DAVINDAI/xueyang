<template>
  <div class="login-container">
    <div class="login-form">
      <h1>登录</h1>
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="80px">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="loginForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="验证码" prop="code">
          <el-input v-model="loginForm.code" placeholder="请输入验证码">
            <template #append>
              <el-button 
                :disabled="countdown > 0" 
                @click="sendCode"
                type="primary"
              >
                {{ countdown > 0 ? `${countdown}秒后重试` : '发送验证码' }}
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="login" :loading="loading" style="width: 100%">
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { sendVerificationCode, login as loginApi } from '../api/authApi';

const router = useRouter();
const loginFormRef = ref(null);
const loading = ref(false);
const countdown = ref(0);

const loginForm = reactive({
  phone: '',
  code: ''
});

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: '请输入6位数字验证码', trigger: 'blur' }
  ]
};

const sendCode = async () => {
  try {
    await loginFormRef.value.validateField('phone');
  } catch (error) {
    return;
  }

  try {
    loading.value = true;
    await sendVerificationCode(loginForm.phone);
    ElMessage.success('验证码已发送');
    startCountdown();
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发送验证码失败');
  } finally {
    loading.value = false;
  }
};

const startCountdown = () => {
  countdown.value = 60;
  const timer = setInterval(() => {
    countdown.value--;
    if (countdown.value <= 0) {
      clearInterval(timer);
    }
  }, 1000);
};

const login = async () => {
  const validateResult = await loginFormRef.value.validate();
  if (!validateResult) return;

  try {
    loading.value = true;
    const response = await loginApi(loginForm.phone, loginForm.code);
    ElMessage.success('登录成功');
    router.push('/');
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '登录失败');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
}

.login-form {
  width: 400px;
  padding: 30px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-form h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
}
</style>
