// Test de XSS Protection con DOMPurify
// Este archivo puede ser ejecutado en la consola del navegador

console.log('🛡️ Test XSS Protection - DOMPurify');
console.log('='.repeat(50));

const testCases = [
  {
    name: 'Script Injection',
    input: '<script>alert("XSS")</script>Hola',
    dangerous: true
  },
  {
    name: 'Event Handler',
    input: '<img src="x" onerror="alert(\'XSS\')" />Hola',
    dangerous: true
  },
  {
    name: 'JavaScript Protocol',
    input: '<a href="javascript:alert(\'XSS\')">Click</a>Hola',
    dangerous: true
  },
  {
    name: 'Allowed Tags Safe',
    input: '<b>Hola</b> <i>mundo</i>',
    dangerous: false
  },
  {
    name: 'Mixed Attack',
    input: '<div><script>alert("XSS")</script><img src="x" onerror="alert(\'XSS\')" /></div>Hola',
    dangerous: true
  }
];

let passedTests = 0;
let totalTests = testCases.length;

testCases.forEach((test, index) => {
  console.log(`\n💉 Test ${index + 1}: ${test.name}`);
  console.log(`📝 Input: ${test.input}`);
  
  // Sanitizar con configuración del ChatMessage.tsx
  const sanitized = DOMPurify.sanitize(test.input, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'br', 'p'],
    ALLOWED_ATTR: ['href', 'target'],
    ALLOW_DATA_ATTR: false
  });
  
  console.log(`🧹 Sanitized: ${sanitized}`);
  
  // Verificar si todavía contiene patrones peligrosos
  const dangerousPatterns = [
    '<script',
    'javascript:',
    'onerror',
    'onload',
    'onclick',
    'onmouseover',
    '<iframe',
    '<object',
    '<embed',
    'eval(',
    'document.cookie'
  ];
  
  const hasDangerousPatterns = dangerousPatterns.some(pattern => 
    sanitized.toLowerCase().includes(pattern.toLowerCase())
  );
  
  const isClean = test.dangerous ? !hasDangerousPatterns : true;
  
  if (isClean) {
    console.log('✅ PASSED - Content properly sanitized');
    passedTests++;
  } else {
    console.log('❌ FAILED - Dangerous patterns still present');
  }
});

console.log('\n' + '='.repeat(50));
console.log(`📊 Results: ${passedTests}/${totalTests} tests passed`);

if (passedTests === totalTests) {
  console.log('🎉 XSS PROTECTION WORKING CORRECTLY');
} else {
  console.log('🚨 XSS PROTECTION NEEDS ATTENTION');
}