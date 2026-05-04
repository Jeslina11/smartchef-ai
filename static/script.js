// TAB SWITCH
function switchTab(tab, btn) {
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));

  document.getElementById('tab-' + tab).classList.add('active');
  btn.classList.add('active');
}

// OPEN CAMERA TAB + AUTO START
function openCameraTab(btn) {
  switchTab('camera', btn);
  startCamera();
}

// PREVIEW UPLOAD
function handleFile(input) {
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = function(e) {
      document.getElementById('preview-img').src = e.target.result;
      document.getElementById('preview-container').style.display = 'block';
    }
    reader.readAsDataURL(input.files[0]);
  }
}

// CAMERA
let stream = null;

async function startCamera() {
  try {
    const video = document.getElementById('video');

    stream = await navigator.mediaDevices.getUserMedia({ video: true });

    video.srcObject = stream;
    video.style.display = "block";

  } catch (err) {
    alert("Kamera tidak bisa diakses: " + err);
  }
}

// CAPTURE + SUBMIT
function captureAndSubmit() {
  const video = document.getElementById('video');
  const canvas = document.createElement('canvas');

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  canvas.getContext('2d').drawImage(video, 0, 0);

  const dataURL = canvas.toDataURL('image/jpeg');

  document.getElementById('camera_data').value = dataURL;

  document.getElementById("camera_form").submit();
}

function toggleMenu() {
    const nav = document.getElementById("navLinks");
    nav.classList.toggle("active");
}