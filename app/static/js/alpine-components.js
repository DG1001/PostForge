// Alpine.js components for PostForge

// Post Editor Component
function postEditor() {
    return {
        post: {
            title: '',
            content: '',
            hashtags: '',
            notes: '',
            scheduledDate: '',
            images: []
        },
        charCount: 0,
        maxChars: 3000,
        dragActive: false,
        
        init() {
            this.$watch('post.content', value => {
                this.charCount = value.length;
            });
        },
        
        handleDrop(event) {
            event.preventDefault();
            this.dragActive = false;
            const files = Array.from(event.dataTransfer.files);
            this.uploadImages(files);
        },
        
        uploadImages(files) {
            const formData = new FormData();
            files.forEach(file => formData.append('images', file));
            
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
                             document.querySelector('input[name="csrf_token"]')?.value;
            
            // Add CSRF token to form data
            if (csrfToken) {
                formData.append('csrf_token', csrfToken);
            }
            
            // HTMX Upload
            htmx.ajax('POST', '/upload/images', {
                values: formData,
                target: '#image-gallery'
            });
        },
        
        removeImage(imageId) {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
                             document.querySelector('input[name="csrf_token"]')?.value;
            
            htmx.ajax('DELETE', `/upload/images/${imageId}/delete`, {
                headers: { 'X-CSRFToken': csrfToken },
                target: '#image-gallery'
            });
        }
    }
}

// PDF Upload Component
function pdfUpload() {
    return {
        dragActive: false,
        uploading: false,
        progress: 0,
        preview: [],
        
        handlePdfDrop(event) {
            event.preventDefault();
            this.dragActive = false;
            const files = Array.from(event.dataTransfer.files);
            const pdfFiles = files.filter(f => f.type === 'application/pdf');
            
            if (pdfFiles.length > 0) {
                this.uploadPdf(pdfFiles[0]);
            }
        },
        
        uploadPdf(file) {
            this.uploading = true;
            const formData = new FormData();
            formData.append('pdf', file);
            
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
                             document.querySelector('input[name="csrf_token"]')?.value;
            
            htmx.ajax('POST', '/upload/pdf', {
                values: formData,
                headers: { 'X-CSRFToken': csrfToken },
                target: '#pdf-preview',
                indicator: '#upload-progress'
            }).then(() => {
                this.uploading = false;
            });
        }
    }
}

// Image Upload Component
function imageUpload(postId) {
    return {
        dragActive: false,
        uploading: false,
        
        handleDrop(event) {
            event.preventDefault();
            this.dragActive = false;
            const files = Array.from(event.dataTransfer.files);
            this.uploadImages(files);
        },
        
        handleFileSelect(event) {
            const files = Array.from(event.target.files);
            this.uploadImages(files);
        },
        
        uploadImages(files) {
            if (!files.length) return;
            
            this.uploading = true;
            const formData = new FormData();
            
            files.forEach(file => {
                formData.append('images', file);
            });
            
            if (postId) {
                formData.append('post_id', postId);
            }
            
            // Get CSRF token from meta tag or form and add to form data
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
                             document.querySelector('input[name="csrf_token"]')?.value;
            
            if (csrfToken) {
                formData.append('csrf_token', csrfToken);
            }
            
            htmx.ajax('POST', '/upload/images', {
                values: formData,
                target: '#image-gallery'
            }).then(() => {
                this.uploading = false;
            });
        }
    }
}

// Search Component
function searchComponent() {
    return {
        query: '',
        results: [],
        isOpen: false,
        
        search() {
            if (this.query.length < 2) {
                this.results = [];
                this.isOpen = false;
                return;
            }
            
            fetch(`/posts/search?q=${encodeURIComponent(this.query)}`)
                .then(response => response.json())
                .then(data => {
                    this.results = data;
                    this.isOpen = true;
                });
        },
        
        selectResult(result) {
            window.location.href = `/posts/${result.id}/edit`;
        }
    }
}

// Notification Component
function notificationComponent() {
    return {
        notifications: [],
        
        addNotification(message, type = 'info') {
            const notification = {
                id: Date.now(),
                message: message,
                type: type
            };
            
            this.notifications.push(notification);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                this.removeNotification(notification.id);
            }, 5000);
        },
        
        removeNotification(id) {
            this.notifications = this.notifications.filter(n => n.id !== id);
        }
    }
}

// Global utility functions
window.copyToClipboard = function(text) {
    navigator.clipboard.writeText(text).then(function() {
        // Show success notification
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded shadow-lg z-50';
        notification.textContent = 'In Zwischenablage kopiert!';
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    });
};

window.copyPostForLinkedIn = function(postId, text, imageCount) {
    // Copy text to clipboard
    navigator.clipboard.writeText(text).then(function() {
        // Show success notification
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded shadow-lg z-50';
        notification.textContent = 'Text in Zwischenablage kopiert!';
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
        
        // If there are images, show the modal
        if (imageCount > 0) {
            loadImagesForDownload(postId);
            // Use a small delay to ensure images are loaded before showing modal
            setTimeout(() => {
                const modal = document.getElementById('imageModal');
                if (modal) {
                    // Try multiple approaches to show the modal
                    modal.classList.remove('hidden');
                    modal.style.display = 'flex';
                    modal.style.visibility = 'visible';
                    modal.style.opacity = '1';
                    modal.style.zIndex = '9999';
                    modal.style.position = 'fixed';
                    modal.style.top = '0';
                    modal.style.left = '0';
                    modal.style.right = '0';
                    modal.style.bottom = '0';
                    
                }
            }, 100);
        }
    });
};

window.loadImagesForDownload = function(postId) {
    fetch(`/posts/${postId}/images`)
        .then(response => response.json())
        .then(images => {
            const container = document.getElementById('imageDownloadList');
            if (!container) return;
            
            container.innerHTML = '';
            
            images.forEach((image, index) => {
                const imageDiv = document.createElement('div');
                imageDiv.className = 'flex items-center justify-between p-3 border border-gray-200 rounded';
                imageDiv.innerHTML = `
                    <div class="flex items-center space-x-3">
                        <img src="/static/uploads/images/${image.filename}" 
                             alt="${image.original_filename}" 
                             class="w-12 h-12 object-cover rounded">
                        <div>
                            <p class="font-medium text-gray-900">${image.original_filename}</p>
                            <p class="text-sm text-gray-500">${formatFileSize(image.file_size)}</p>
                        </div>
                    </div>
                    <a href="/static/uploads/images/${image.filename}" 
                       download="${image.original_filename}"
                       class="btn-secondary text-sm">
                        Herunterladen
                    </a>
                `;
                container.appendChild(imageDiv);
            });
        })
        .catch(error => {
            console.error('Error loading images:', error);
        });
};

window.closeImageModal = function() {
    const modal = document.getElementById('imageModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.style.display = 'none'; // Force hide
    }
};

window.formatFileSize = function(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};

window.confirmDelete = function(message) {
    return confirm(message || 'Sind Sie sicher, dass Sie diesen Eintrag löschen möchten?');
};

// Initialize components globally
document.addEventListener('alpine:init', () => {
    Alpine.data('postEditor', postEditor);
    Alpine.data('pdfUpload', pdfUpload);
    Alpine.data('imageUpload', imageUpload);
    Alpine.data('searchComponent', searchComponent);
    Alpine.data('notificationComponent', notificationComponent);
});