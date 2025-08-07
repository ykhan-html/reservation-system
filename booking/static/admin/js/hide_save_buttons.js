// Django Admin에서 추가 저장 버튼들을 숨기는 스크립트
document.addEventListener('DOMContentLoaded', function() {
    // '저장 및 다른이름으로 추가' 버튼 숨기기
    const saveAddAnotherButton = document.querySelector('input[name="_addanother"]');
    if (saveAddAnotherButton) {
        saveAddAnotherButton.style.display = 'none';
    }
    
    // '저장 및 편집 계속' 버튼 숨기기
    const saveContinueButton = document.querySelector('input[name="_continue"]');
    if (saveContinueButton) {
        saveContinueButton.style.display = 'none';
    }
    
    // 버튼의 부모 요소도 숨기기 (레이아웃 정리를 위해)
    const saveButtonsContainer = document.querySelector('.submit-row');
    if (saveButtonsContainer) {
        const buttons = saveButtonsContainer.querySelectorAll('input[type="submit"]');
        buttons.forEach(function(button) {
            if (button.name === '_addanother' || button.name === '_continue') {
                button.style.display = 'none';
            }
        });
    }
}); 