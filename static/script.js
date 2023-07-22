let textareas = document.getElementsByTagName('textarea')

for (let textarea of textareas) {
    textarea.addEventListener('blur', trim)
}

function trim() {
    this.value = this.value.trim()
    this.dispatchEvent(new Event('input'));
}