<template>
  <div class="flex justify-center items-center min-h-screen bg-gray-100">
    <div class="bg-white p-6 rounded shadow w-80">
      <h1 class="text-xl font-bold mb-4 text-center">Register</h1>
      
      <input
        v-model="username"
        placeholder="Username"
        class="mb-3 p-2 border w-full rounded"
      />

      <input
        v-model="password"
        type="password"
        placeholder="Password"
        class="mb-3 p-2 border w-full rounded"
      />

      <input
        v-model="confirmPassword"
        type="password"
        placeholder="Confirm Password"
        class="mb-4 p-2 border w-full rounded"
      />

      <button
        @click="handleRegister"
        class="bg-green-500 text-white p-2 w-full rounded hover:bg-green-600"
      >
        Register
      </button>

      <p v-if="errorMsg" class="text-red-500 text-sm mt-3 text-center">
        {{ errorMsg }}
      </p>
      <p class="text-center text-sm mt-4">
        Already have an account? 
        <router-link to="/login" class="text-blue-500 hover:underline">Login</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const confirmPassword = ref('') // เพิ่มสำหรับยืนยันรหัสผ่าน
const errorMsg = ref('')
const router = useRouter()

const handleRegister = async () => {
  errorMsg.value = '' // เคลียร์ข้อความผิดพลาดเดิม

  // ตรวจสอบว่ารหัสผ่านตรงกันหรือไม่
  if (password.value !== confirmPassword.value) {
    errorMsg.value = 'Passwords do not match.'
    return
  }

  // ตรวจสอบความยาวของรหัสผ่าน (ตัวอย่าง: ต้องมีอย่างน้อย 6 ตัวอักษร)
  if (password.value.length < 6) {
    errorMsg.value = 'Password must be at least 6 characters long.'
    return
  }
  
  // ตรวจสอบว่ามีชื่อผู้ใช้และรหัสผ่านหรือไม่
  if (!username.value || !password.value) {
    errorMsg.value = 'Please fill in all fields.'
    return;
  }

  try {
    const res = await axios.post('http://localhost:5000/api/register', { // เปลี่ยน endpoint เป็น /api/register
      username: username.value,
      password: password.value
    })

    // ถ้าลงทะเบียนสำเร็จ อาจจะ redirect ไปหน้า login หรือ dashboard ทันที
    // ตัวอย่างนี้จะ redirect ไปหน้า login เพื่อให้ผู้ใช้ล็อกอิน
    alert(res.data.msg || 'Registration successful! Please log in.') // แสดงข้อความสำเร็จ
    router.push('/login')
  } catch (err) {
    // ดึงข้อความ error จาก backend หรือแสดงข้อความทั่วไป
    errorMsg.value =
      err.response?.data?.msg || 'Registration failed. Please try again.'
  }
}
</script>