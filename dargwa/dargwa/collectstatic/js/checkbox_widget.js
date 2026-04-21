document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.checkbox-widget-container').forEach(initCheckboxWidget);
});

function initCheckboxWidget(container) {
    const selectAllCheckbox = container.querySelector('.select-all-checkbox');
    const optionCheckboxes = container.querySelectorAll('.option-checkbox');

    if (!selectAllCheckbox) return;

    function updateSelectAllState() {
        const totalOptions = optionCheckboxes.length;
        const checkedCount = Array.from(optionCheckboxes).filter(cb => cb.checked).length;

        if (totalOptions === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        } else if (checkedCount === totalOptions) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else if (checkedCount > 0 && checkedCount < totalOptions) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        }
    }

    selectAllCheckbox.addEventListener('change', function(e) {
        const isChecked = this.checked;

        optionCheckboxes.forEach(cb => {
            cb.checked = isChecked;
            const event = new Event('change', { bubbles: true });
            cb.dispatchEvent(event);
        });

        this.indeterminate = false;
    });

    optionCheckboxes.forEach(cb => {
        cb.addEventListener('change', function() {
            updateSelectAllState();
        });
    });

    updateSelectAllState();
}
