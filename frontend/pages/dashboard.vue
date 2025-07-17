<template>
  <div class="p-6 max-w-3xl mx-auto">
    <h1 class="text-2xl font-bold mb-4">My Notes</h1>

    <div class="mb-4">
      <input
        v-model="searchTerm"
        @input="debouncedSearch"
        placeholder="Search notes by title or content..."
        class="border p-2 w-full rounded-md"
      />
    </div>

    <div class="flex gap-2 mb-4">
      <input v-model="title" placeholder="Title" class="border p-2 w-1/3 rounded-md" />
      <input v-model="content" placeholder="Content" class="border p-2 flex-1 rounded-md" />
      <button @click="createNote" class="bg-green-500 text-white p-2 rounded-md hover:bg-green-600">Add Note</button>
    </div>

    <p v-if="notes.length === 0 && !loading" class="text-center text-gray-500 mt-8">
      No notes found. Create a new one!
    </p>

    <NoteCard
      v-for="note in filteredNotes"
      :key="note.id"
      :note="note"
      @delete="deleteNote"
    />
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted, computed } from 'vue' // เพิ่ม computed
import NoteCard from '../components/NoteCard.vue'; // ตรวจสอบ path ที่ถูกต้องของ NoteCard

const title = ref('')
const content = ref('')
const notes = ref([])
const searchTerm = ref('') // เพิ่ม state สำหรับคำค้นหา
const loading = ref(true) // เพิ่ม state สำหรับการโหลด
let searchTimeout = null; // สำหรับ Debounce

// เราจะทำการ filter notes ทางฝั่ง frontend เพื่อความง่าย
// หรือคุณสามารถส่ง searchTerm ไปให้ backend filter ก็ได้ (แนะนำสำหรับข้อมูลเยอะๆ)

const fetchNotes = async () => {
  loading.value = true;
  const token = localStorage.getItem('token')
  try {
    const res = await axios.get('http://localhost:5000/api/notes', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    notes.value = res.data
  } catch (error) {
    console.error("Error fetching notes:", error);
    // จัดการ error เช่น redirect ไปหน้า login ถ้า token หมดอายุ
  } finally {
    loading.value = false;
  }
}

const createNote = async () => {
  const token = localStorage.getItem('token')
  // ตรวจสอบว่ามีข้อมูลหรือไม่
  if (!title.value.trim() || !content.value.trim()) {
    alert('Please enter both title and content for the note.');
    return;
  }
  try {
    await axios.post('http://localhost:5000/api/notes', {
      title: title.value,
      content: content.value
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    title.value = ''
    content.value = ''
    fetchNotes() // โหลด notes ใหม่หลังจากสร้างสำเร็จ
  } catch (e) {
    console.error('Create note failed:', e)
    alert('Failed to create note. Please try again.');
  }
}

const deleteNote = async (id) => {
  const token = localStorage.getItem('token')
  try {
    await axios.delete(`http://localhost:5000/api/notes/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    fetchNotes() // โหลด notes ใหม่หลังจากลบสำเร็จ
  } catch (e) {
    console.error('Delete note failed:', e)
    alert('Failed to delete note. Please try again.');
  }
}

// === ส่วนเพิ่มเติมสำหรับการค้นหา ===

// ใช้ Computed Property เพื่อ Filter Notes ตาม searchTerm
const filteredNotes = computed(() => {
  if (!searchTerm.value) {
    return notes.value; // ถ้าไม่มีคำค้นหา ให้แสดง notes ทั้งหมด
  }
  const lowerCaseSearchTerm = searchTerm.value.toLowerCase();
  return notes.value.filter(note =>
    (note.title && note.title.toLowerCase().includes(lowerCaseSearchTerm)) ||
    (note.content && note.content.toLowerCase().includes(lowerCaseSearchTerm))
  );
});

// Debounce function เพื่อให้ fetchNotes ถูกเรียกเมื่อผู้ใช้หยุดพิมพ์
const debouncedSearch = () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    // ในกรณีที่คุณต้องการให้ backend ค้นหา ให้เรียก fetchNotes() ที่นี่
    // แต่ในโค้ดนี้เราใช้ filteredNotes ที่เป็น computed property อยู่แล้ว
    // ดังนั้นการอัปเดต searchTerm.value จะทำให้ filteredNotes ถูกคำนวณใหม่เอง
    // หากต้องการค้นหาผ่าน API จริงๆ จะเปลี่ยนเป็น fetchNotes(searchTerm.value)
  }, 300); // 300ms delay
};


onMounted(fetchNotes)
</script>