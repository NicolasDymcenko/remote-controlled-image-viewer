<template>
  <div class="image-viewer" tabindex="0" @keydown="handleKeyDown" ref="viewer">
    <div v-if="paket_id !== '-1' && images.length > 0" class="image-info">Bild {{ currentIndex + 1 }} von {{ images.length }}</div>
    <div class="image-container" 
         ref="container" 
         @wheel="handleZoom" 
         @mousedown="startDrag" 
         @mousemove="drag" 
         @mouseup="endDrag" 
         @dragstart.prevent>
      <img v-if="currentImage" 
           :src="currentImage" 
           :style="imageStyle" 
           ref="image" 
           alt="Aktuelles Bild" 
           @load="resetView"
           draggable="false" />
      <div v-else-if="paket_id !== '-1'" class="no-image-message">Kein Bild für diese Paket ID vorhanden.</div>
    </div>
    <div v-if="paket_id !== '-1'" class="preview-container">
      <div class="preview-images">
        <img v-for="(image, index) in images" 
             :key="index" 
             :src="image" 
             :class="{ 'active': index === currentIndex }"
             @click="selectImage(index)"
             alt="Vorschaubild" />
      </div>
    </div>
    <div class="controls">
      <button @click="showShortcuts" title="Hilfe anzeigen (H)" class="help-button">
        <i class="fas fa-question"></i>
      </button>
      <div class="main-controls">
        <button @click="prevImage" title="Vorheriges Bild (A)">
          <i class="fas fa-chevron-left"></i>
        </button>
        <button @click="nextImage" title="Nächstes Bild (D)">
          <i class="fas fa-chevron-right"></i>
        </button>
        <button @click="zoomIn" title="Vergrößern (+)">
          <i class="fas fa-search-plus"></i>
        </button>
        <button @click="zoomOut" title="Verkleinern (-)">
          <i class="fas fa-search-minus"></i>
        </button>
        <button @click="rotateLeft" title="Nach links drehen (Q)">
          <i class="fas fa-undo"></i>
        </button>
        <button @click="rotateRight" title="Nach rechts drehen (E)">
          <i class="fas fa-redo"></i>
        </button>
        <button @click="resetView" title="Ansicht zurücksetzen (R)">
          <i class="fas fa-sync-alt"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const paket_id = route.params.paketid;
const images = ref([]);
const currentIndex = ref(0);
const scale = ref(1);
const rotation = ref(0);
const dragStart = ref({ x: 0, y: 0 });
const position = ref({ x: 0, y: 0 });
const isDragging = ref(false);

const container = ref(null);
const image = ref(null);
const viewer = ref(null);

const currentImage = computed(() => images.value[currentIndex.value]);

const imageStyle = computed(() => ({
  transform: `translate(${position.value.x}px, ${position.value.y}px) scale(${scale.value}) rotate(${rotation.value}deg)`,
  transition: isDragging.value ? 'none' : 'transform 0.1s ease-out',
  pointerEvents: 'none',
}));

onMounted(async () => {
  if (paket_id !== '-1') {
    try {
      const response = await axios.get(`http://192.168.2.128:5000/api/${paket_id}`);
      images.value = response.data.map(base64Image => `data:image/jpeg;base64,${base64Image}`);
      viewer.value.focus();
    } catch (error) {
      console.error('Error fetching images:', error);
    }
  }

  document.addEventListener('mousemove', drag);
  document.addEventListener('mouseup', endDrag);
});

onUnmounted(() => {
  document.removeEventListener('mousemove', drag);
  document.removeEventListener('mouseup', endDrag);
});

const selectImage = (index) => {
  currentIndex.value = index;
  resetView();
};

const nextImage = () => {
  currentIndex.value = (currentIndex.value + 1) % images.value.length;
  resetView();
};

const prevImage = () => {
  currentIndex.value = (currentIndex.value - 1 + images.value.length) % images.value.length;
  resetView();
};

const zoomFactor = 1.1;
const minZoom = 0.1;
const maxZoom = 5;

const zoomIn = () => {
  scale.value = Math.min(scale.value * zoomFactor, maxZoom);
};

const zoomOut = () => {
  scale.value = Math.max(scale.value / zoomFactor, minZoom);
};

const rotateLeft = () => {
  rotation.value -= 90;
};

const rotateRight = () => {
  rotation.value += 90;
};

const resetView = () => {
  scale.value = 1;
  rotation.value = 0;
  position.value = { x: 0, y: 0 };
};

const handleZoom = (e) => {
  e.preventDefault();
  if (e.deltaY < 0) {
    zoomIn();
  } else {
    zoomOut();
  }
};

const startDrag = (e) => {
  e.preventDefault();
  isDragging.value = true;
  dragStart.value = { x: e.clientX - position.value.x, y: e.clientY - position.value.y };
};

const drag = (e) => {
  if (isDragging.value) {
    position.value = {
      x: e.clientX - dragStart.value.x,
      y: e.clientY - dragStart.value.y,
    };
  }
};

const endDrag = () => {
  isDragging.value = false;
};

const moveStep = 50;

const moveImage = (dx, dy) => {
  position.value.x += dx;
  position.value.y += dy;
};

const handleKeyDown = (e) => {
  switch (e.key.toLowerCase()) {
    case 'a': prevImage(); break;
    case 'd': nextImage(); break;
    case 'q': rotateLeft(); break;
    case 'e': rotateRight(); break;
    case '+': zoomIn(); break;
    case '-': zoomOut(); break;
    case 'r': resetView(); break;
    case 'h': showShortcuts(); break;
    case 'arrowleft': moveImage(moveStep, 0); break;
    case 'arrowright': moveImage(-moveStep, 0); break;
    case 'arrowup': moveImage(0, moveStep); break;
    case 'arrowdown': moveImage(0, -moveStep); break;
  }
};

const showShortcuts = () => {
  alert(`
    Tastaturkürzel:
    A: Vorheriges Bild
    D: Nächstes Bild
    Q: Nach links drehen
    E: Nach rechts drehen
    +: Vergrößern
    -: Verkleinern
    R: Ansicht zurücksetzen
    H: Diese Hilfe anzeigen
    Pfeiltasten: Bild bewegen (invertiert)
  `);
};
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css');

.image-viewer {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #1a1a1a;
  color: white;
  position: relative;
  outline: none;
}

.image-container {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  cursor: grab;
  user-select: none;
  position: relative;
}

.image-container:active {
  cursor: grabbing;
}

.no-image-message {
  font-size: 18px;
  text-align: center;
}

.preview-container {
  position: absolute;
  left: 0;
  bottom: 4rem;
  display: inline-block;
  z-index: 5;
}

.preview-images {
  display: flex;
  gap: 10px;
  padding: 10px;
  background-color: rgba(0, 0, 0, 0.5);
  border-top-right-radius: 10px;
  border-bottom-right-radius: 10px;
}

.preview-images img {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 5px;
  opacity: 0.5;
  transition: opacity 0.3s, transform 0.3s;
  cursor: pointer;
}

.preview-images img:hover {
  opacity: 0.8;
  transform: scale(1.05);
}

.preview-images img.active {
  opacity: 1;
  border: 2px solid white;
}

img {
  max-width: 100%;
  max-height: 100%;
}

.controls {
  padding: 5px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 4;
}

.main-controls {
  display: flex;
  gap: 15px;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

button {
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.2s;
  font-size: 18px;
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
}

button:hover {
  background-color: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

button:active {
  transform: scale(0.95);
}

.help-button {
  margin-right: auto;
}

.image-info {
  position: absolute;
  top: 15px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 14px;
  background-color: rgba(0, 0, 0, 0.5);
  padding: 5px 10px;
  border-radius: 15px;
  z-index: 6;
}
</style>
