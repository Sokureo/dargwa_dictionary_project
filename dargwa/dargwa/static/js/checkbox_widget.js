document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.tags-dropdown-widget').forEach(initTagsDropdown);
});

function initTagsDropdown(widget) {
    const widgetId = widget.dataset.name;
    const trigger = document.getElementById(`${widgetId}_trigger`);
    const tagsContainer = document.getElementById(`${widgetId}_tags_container`);
    const dropdown = document.getElementById(`${widgetId}_dropdown`);
    const selectAllCheckbox = document.getElementById(`${widgetId}_select_all`);
    const optionCheckboxes = widget.querySelectorAll('.option-checkbox');
    const tagsList = widget.querySelector('.tags-list');
    const hiddenSelect = widget.querySelector('select');

    function toggleDropdown(show) {
        if (show === undefined) {
            dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        } else {
            dropdown.style.display = show ? 'block' : 'none';
        }
    }

    if (tagsContainer) {
        tagsContainer.addEventListener('click', function(e) {
            if (e.target.classList && e.target.classList.contains('tag-remove')) {
                e.stopPropagation();
                return;
            }
            toggleDropdown();
        });
    }
    
    if (trigger) {
        trigger.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleDropdown();
        });
    }
    
    document.addEventListener('click', function(e) {
        if (!widget.contains(e.target)) {
            if (dropdown) dropdown.style.display = 'none';
        }
    });

    function updateTags() {
        if (!tagsList) return;
        
        const selectedOptions = Array.from(optionCheckboxes).filter(cb => cb.checked);
        tagsList.innerHTML = '';
        
        selectedOptions.forEach(cb => {
            const label = cb.dataset.label || 
                          (cb.parentElement ? cb.parentElement.querySelector('span')?.innerText : null) || 
                          cb.value;
            
            const tag = document.createElement('span');
            tag.className = 'tag';
            tag.dataset.value = cb.value;
            tag.innerHTML = `${label} <span class="tag-remove" data-value="${cb.value}">×</span>`;
            tagsList.appendChild(tag);
        });
        
        widget.querySelectorAll('.tag-remove').forEach(btn => {
            btn.removeEventListener('click', handleTagRemove);
            btn.addEventListener('click', handleTagRemove);
        });
        
        updateHiddenSelect();
    }
    
    function handleTagRemove(e) {
        e.stopPropagation();
        const value = this.dataset.value;
        const checkbox = Array.from(optionCheckboxes).find(cb => cb.value === value);
        if (checkbox) {
            checkbox.checked = false;
            checkbox.dispatchEvent(new Event('change'));
            updateTags();
            updateSelectAllState();
        }
    }
    
    function updateHiddenSelect() {
        if (!hiddenSelect) return;
        hiddenSelect.innerHTML = '';
        optionCheckboxes.forEach(cb => {
            if (cb.checked) {
                const option = document.createElement('option');
                option.value = cb.value;
                option.selected = true;
                option.textContent = cb.dataset.label || cb.value;
                hiddenSelect.appendChild(option);
            }
        });
    }
    
    function updateSelectAllState() {
        if (!selectAllCheckbox) return;
        const total = optionCheckboxes.length;
        const checked = Array.from(optionCheckboxes).filter(cb => cb.checked).length;
        
        if (checked === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        } else if (checked === total) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        }
    }
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            optionCheckboxes.forEach(cb => {
                cb.checked = isChecked;
                cb.dispatchEvent(new Event('change'));
            });
            updateTags();
            updateSelectAllState();
        });
    }
    
    optionCheckboxes.forEach(cb => {
        cb.addEventListener('change', function() {
            if (selectAllCheckbox && selectAllCheckbox.checked && !this.checked) {
                selectAllCheckbox.checked = false;
                selectAllCheckbox.indeterminate = false;
            }
            updateTags();
            updateSelectAllState();
        });
    });
    
    updateTags();
    updateSelectAllState();
}
