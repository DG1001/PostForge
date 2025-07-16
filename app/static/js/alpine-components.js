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
            
            // HTMX Upload
            htmx.ajax('POST', '/upload/images', {
                values: formData,
                target: '#image-gallery'
            });
        },
        
        removeImage(imageId) {
            htmx.ajax('DELETE', `/upload/images/${imageId}/delete`, {
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
            
            htmx.ajax('POST', '/upload/pdf', {
                values: formData,
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