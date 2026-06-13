// Language switching functionality for AarogyaLink - Fixed Version
let currentLanguage = 'en';
let isLanguageDropdownOpen = false;

// Multilingual content
const translations = {
    en: {
        greeting: "Hi! I'm Dr. AarogyaLink, your AI health buddy. Tell me what's bothering you and I'll ask a few quick questions to help out. 😊\n\nRemember: For serious concerns, always see a real doctor!",
        name: "English",
        placeholder: "Tell me what's bothering you... e.g. 'Bad headache since this morning, right side, feels throbbing, also nauseous'",
        quickPrompts: {
            headache: "🤕 Headache",
            fever: "🤒 Fever", 
            stomach: "😷 Stomach Pain",
            cough: "😷 Cough/Cold",
            fatigue: "😴 Fatigue",
            injury: "🤕 Injury/Pain"
        },
        buttons: {
            send: "Send",
            record: "Start Recording",
            analyze: "Analyze Image",
            startAI: "Start AI Analysis"
        }
    },
    hi: {
        // Navigation and Header
        brandName: "आरोग्यलिंक",
        brandSubtitle: "आपका व्यक्तिगत स्वास्थ्य साथी",
        navHowItWorks: "यह कैसे काम करता है",
        navTryNow: "अभी आज़माएं",
        navWhyUs: "हमें क्यों चुनें",
        navContact: "संपर्क करें",
        themeToggle: "डार्क",
        
        // Hero Section
        heroTitle: "आपका व्यक्तिगत स्वास्थ्य साथी",
        heroSubtitle: "जब भी आपको ज़रूरत हो, देखभाल से जुड़ें। अपनी स्वास्थ्य संबंधी चिंताओं को सुरक्षित रूप से साझा करें और विशेषज्ञ मार्गदर्शन प्राप्त करें, सब एक ही जगह।",
        tryNowButton: "अभी आज़माएं",
        
        // How It Works Section
        howItWorksTitle: "अपने तरीके से देखभाल से जुड़ें।",
        howItWorksSubtitle: "हमारा प्लेटफ़ॉर्म आपके लिए किसी भी फॉर्मेट में अपनी स्वास्थ्य चिंताओं को साझा करना आसान बनाता है।",
        
        // Method Cards
        textCardTitle: "अपने लक्षणों का वर्णन करें",
        textCardDesc: "बस बताएं कि आपके मन में क्या है। हमारा प्लेटफ़ॉर्म आपके शब्दों का उपयोग करके आपको सही सहायता से जोड़ता है।",
        imageCardTitle: "एक फोटो साझा करें",
        imageCardDesc: "कभी-कभी, एक तस्वीर पूरी कहानी कह देती है। दाने, चोट, या नुस्खे की फोटो लें।",
        voiceCardTitle: "एक त्वरित संदेश रिकॉर्ड करें",
        voiceCardDesc: "टाइप नहीं कर सकते? बस एक वॉयस मैसेज रिकॉर्ड करें और हमारे विशेषज्ञ सुनेंगे और जवाब देंगे।",
        
        // Chat Section
        chatTitle: "आरोग्यलिंक अभी आज़माएं",
        chatSubtitle: "अपनी स्वास्थ्य चिंताओं को उस तरीके से साझा करें जो आपके लिए सबसे अच्छा काम करे",
        
        // Tab Labels
        typeTab: "यहाँ अपनी समस्या टाइप करें",
        imageTab: "छवि के साथ खोजें",
        voiceTab: "कुछ भी कहें",
        
        // Chat Interface
        greeting: "नमस्ते! मैं डॉ. आरोग्यलिंक हूं, आपका AI स्वास्थ्य साथी। मैं विस्तृत चिकित्सा विश्लेषण प्रदान करता हूं जिसमें स्थिति मूल्यांकन, उपचार सुझाव और पेशेवर मार्गदर्शन शामिल है। अपने लक्षण साझा करें और मैं आपको संपूर्ण स्वास्थ्य विश्लेषण दूंगा! 😊\n\nयाद रखें: यह AI-संचालित विश्लेषण है। अंतिम निदान और उपचार के लिए हमेशा स्वास्थ्य पेशेवर से सलाह लें।",
        placeholder: "कृपया अपने लक्षणों का विस्तार से वर्णन करें... उदाहरण के लिए: 'मुझे आज सुबह से तेज़ सिरदर्द है। यह धड़क रहा है और मेरे सिर के दाईं ओर है। मुझे जी भी मिचला रहा है।'",
        quickTip: "त्वरित सुझाव: बताएं कि यह कब शुरू हुआ, दर्द का स्तर (1-10), और क्या इसे बेहतर/बदतर बनाता है",
        quickStartOptions: "त्वरित प्रारंभ विकल्प:",
        
        // Quick Prompts
        quickPrompts: {
            headache: "🤕 सिरदर्द",
            fever: "🤒 बुखार",
            stomach: "😷 पेट दर्द",
            cough: "😷 खांसी/जुकाम",
            fatigue: "😴 थकान", 
            injury: "🤕 चोट/दर्द"
        },
        
        // Image Upload
        imageUploadTitle: "एक मेडिकल छवि अपलोड करें",
        imageUploadDesc: "दाने, चोट, नुस्खे, या परीक्षण परिणामों की तस्वीरें साझा करें",
        chooseImageButton: "छवि फ़ाइल चुनें",
        modelStatus: "🤖 AI मॉडल: लोड हो रहा है...",
        aiAnalysisResults: "🤖 AI विश्लेषण परिणाम",
        imageDescPlaceholder: "अपने लक्षणों या चिंताओं के बारे में कोई अतिरिक्त विवरण जोड़ें...",
        getHealthAdviceButton: "स्वास्थ्य सलाह प्राप्त करें",
        clearButton: "साफ़ करें",
        imageSupportInfo: "📷 समर्थित: JPG, PNG, GIF • अधिकतम आकार: 16MB • छवियों को स्पष्ट और अच्छी रोशनी में रखें",
        aiDisclaimer: "🤖 प्रारंभिक मूल्यांकन के लिए AI का उपयोग करके छवियों का विश्लेषण किया जाता है - हमेशा एक स्वास्थ्य पेशेवर से सलाह लें",
        
        // Voice Recording
        voiceRecordTitle: "अपना संदेश रिकॉर्ड करें",
        voiceRecordSubtitle: "अपनी स्वास्थ्य चिंताओं को रिकॉर्ड करना शुरू करने के लिए क्लिक करें",
        startRecordingButton: "रिकॉर्डिंग शुरू करें",
        uploadAudioText: "या एक ऑडियो फ़ाइल अपलोड करें:",
        chooseAudioButton: "ऑडियो फ़ाइल चुनें",
        voiceInfo: "🎤 स्पष्ट रूप से बोलें और अपने सभी लक्षणों का उल्लेख करें • ऑडियो को सुरक्षित रूप से संसाधित किया जाएगा",
        
        // Why Us Section
        whyUsTitle: "स्वास्थ्य एक साझेदारी है। हम मदद के लिए यहाँ हैं।",
        accessTitle: "24/7 पहुंच",
        accessDesc: "स्वास्थ्य सेवा जो आपके समय के अनुकूल हो, न कि इसके विपरीत। जब भी आपको ज़रूरत हो, उत्तर पाएं।",
        privacyTitle: "गोपनीयता और सुरक्षा",
        privacyDesc: "आपका स्वास्थ्य डेटा बैंक-स्तरीय एन्क्रिप्शन के साथ सुरक्षित है। आपकी गोपनीयता हमारी सर्वोच्च प्राथमिकता है।",
        expertTitle: "विशेषज्ञ मार्गदर्शन",
        expertDesc: "भरोसेमंद सलाह के लिए सत्यापित स्वास्थ्य पेशेवरों के नेटवर्क से जुड़ें।",
        
        // Contact Section
        contactTitle: "संपर्क में रहें",
        contactSubtitle: "सभी गैर-चिकित्सा पूछताछ के लिए, कृपया नीचे दिया गया फॉर्म भरें।",
        namePlaceholder: "आपका नाम",
        emailPlaceholder: "आपका ईमेल",
        messagePlaceholder: "आपका संदेश",
        sendMessageButton: "संदेश भेजें",
        
        // Footer
        footerText: "© 2024 आरोग्यलिंक। सभी अधिकार सुरक्षित।",
        privacyPolicy: "गोपनीयता नीति",
        termsOfService: "सेवा की शर्तें",
        
        // Medical Analysis Terms (Hindi)
        analysisComplete: "विश्लेषण पूर्ण",
        predictedCondition: "अनुमानित स्थिति",
        confidence: "विश्वास",
        detailedMedicalAnalysis: "विस्तृत चिकित्सा विश्लेषण",
        commonSymptoms: "सामान्य लक्षण",
        recommendedTests: "अनुशंसित नैदानिक परीक्षण",
        treatmentOptions: "उपचार विकल्प",
        whenToSeekCare: "तत्काल चिकित्सा सहायता कब लें",
        medicalNote: "नोट: यह एक AI भविष्यवाणी है। सटीक निदान और उपचार योजना के लिए चिकित्सा पेशेवर से सलाह लें।",
        important: "महत्वपूर्ण",
        
        // Additional missing translations
        getStarted: "शुरू करें",
        quickTip: "💡 <strong>तेज़ सुझाव:</strong> बताएं कि यह कब शुरू हुआ, दर्द का स्तर (1-10), और क्या इसे बेहतर/माड़ा बनाता है",
        
        // Quick prompt button translations
        headache: "🤕 सिरदर्द",
        fever: "🤒 बुखार",
        stomach: "😷 पेट दर्द",
        cough: "😷 खांसी/ज़ुकाम",
        fatigue: "😴 थकान",
        injury: "🤕 चोट/दर्द",
        
        // Buttons
        buttons: {
            send: "भेजें",
            record: "रिकॉर्डिंग शुरू करें",
            analyze: "छवि का विश्लेषण करें",
            startAI: "AI विश्लेषण शुरू करें"
        },
        
        name: "हिंदी"
    },
    pa: {
        // Navigation and Header
        brandName: "ਆਰੋਗਿਆਲਿੰਕ",
        brandSubtitle: "ਤੁਹਾਡਾ ਨਿੱਜੀ ਸਿਹਤ ਸਾਥੀ",
        navLinks: {
            howItWorks: "ਇਹ ਕਿਵੇਂ ਕੰਮ ਕਰਦਾ ਹੈ",
            tryNow: "ਹੁਣੇ ਕੋਸ਼ਿਸ਼ ਕਰੋ",
            whyUs: "ਸਾਨੂੰ ਕਿਉਂ ਚੁਣੋ",
            contact: "ਸੰਪਰਕ ਕਰੋ"
        },
        themeToggle: "ਹਨੇਰਾ",
        getStarted: "ਸ਼ੁਰੂ ਕਰੋ",
        
        // Hero Section
        heroTitle: "ਤੁਹਾਡਾ ਨਿੱਜੀ ਸਿਹਤ ਸਾਥੀ",
        heroSubtitle: "ਜਦੋਂ ਵੀ ਤੁਹਾਨੂੰ ਲੋੜ ਹੋਵੇ, ਦੇਖਭਾਲ ਨਾਲ ਜੁੜੋ। ਆਪਣੀਆਂ ਸਿਹਤ ਸੰਬੰਧੀ ਚਿੰਤਾਵਾਂ ਨੂੰ ਸੁਰੱਖਿਅਤ ਰੂਪ ਨਾਲ ਸਾਂਝਾ ਕਰੋ ਅਤੇ ਮਾਹਰ ਮਾਰਗਦਰਸ਼ਨ ਪ੍ਰਾਪਤ ਕਰੋ, ਸਭ ਇੱਕ ਹੀ ਜਗ੍ਹਾ।",
        tryNowButton: "ਹੁਣੇ ਕੋਸ਼ਿਸ਼ ਕਰੋ",
        
        // How It Works Section
        howItWorksTitle: "ਆਪਣੇ ਤਰੀਕੇ ਨਾਲ ਦੇਖਭਾਲ ਨਾਲ ਜੁੜੋ।",
        howItWorksSubtitle: "ਸਾਡਾ ਪਲੇਟਫਾਰਮ ਤੁਹਾਡੇ ਲਈ ਕਿਸੇ ਵੀ ਫਾਰਮੈਟ ਵਿੱਚ ਆਪਣੀਆਂ ਸਿਹਤ ਚਿੰਤਾਵਾਂ ਸਾਂਝੀਆਂ ਕਰਨਾ ਆਸਾਨ ਬਣਾਉਂਦਾ ਹੈ।",
        
        // Method Cards
        textCardTitle: "ਆਪਣੇ ਲੱਛਣਾਂ ਦਾ ਵਰਣਨ ਕਰੋ",
        textCardDesc: "ਬਸ ਦੱਸੋ ਕਿ ਤੁਹਾਡੇ ਮਨ ਵਿੱਚ ਕੀ ਹੈ। ਸਾਡਾ ਪਲੇਟਫਾਰਮ ਤੁਹਾਡੇ ਸ਼ਬਦਾਂ ਦੀ ਵਰਤੋਂ ਕਰਕੇ ਤੁਹਾਨੂੰ ਸਹੀ ਸਹਾਇਤਾ ਨਾਲ ਜੋੜਦਾ ਹੈ।",
        imageCardTitle: "ਇੱਕ ਫੋਟੋ ਸਾਂਝੀ ਕਰੋ",
        imageCardDesc: "ਕਈ ਵਾਰ, ਇੱਕ ਤਸਵੀਰ ਪੂਰੀ ਕਹਾਣੀ ਦੱਸ ਦਿੰਦੀ ਹੈ। ਪੱਤਰ, ਸੱਟ, ਜਾਂ ਨੁਸਖੇ ਦੀ ਫੋਟੋ ਲਓ।",
        voiceCardTitle: "ਇੱਕ ਤੇਜ਼ ਸੰਦੇਸ਼ ਰਿਕਾਰਡ ਕਰੋ",
        voiceCardDesc: "ਟਾਈਪ ਨਹੀਂ ਕਰ ਸਕਦੇ? ਬਸ ਇੱਕ ਵਾਇਸ ਮੈਸੇਜ ਰਿਕਾਰਡ ਕਰੋ ਅਤੇ ਸਾਡੇ ਮਾਹਰ ਸੁਣਨਗੇ ਅਤੇ ਜਵਾਬ ਦੇਣਗੇ।",
        
        // Chat Section
        chatTitle: "ਆਰੋਗਿਆਲਿੰਕ ਹੁਣੇ ਕੋਸ਼ਿਸ਼ ਕਰੋ",
        chatSubtitle: "ਆਪਣੀਆਂ ਸਿਹਤ ਚਿੰਤਾਵਾਂ ਨੂੰ ਉਸ ਤਰੀਕੇ ਨਾਲ ਸਾਂਝਾ ਕਰੋ ਜੋ ਤੁਹਾਡੇ ਲਈ ਸਭ ਤੋਂ ਵਧੀਆ ਕੰਮ ਕਰੇ",
        
        // Tab Labels
        typeTab: "ਇੱਥੇ ਆਪਣੀ ਸਮੱਸਿਆ ਟਾਈਪ ਕਰੋ",
        imageTab: "ਤਸਵੀਰ ਨਾਲ ਖੋਜੋ",
        voiceTab: "ਕੁਝ ਵੀ ਕਹੋ",
        
        // Chat Interface
        greeting: "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਡਾ. ਆਰੋਗਿਆਲਿੰਕ ਹਾਂ, ਤੁਹਾਡਾ AI ਸਿਹਤ ਸਾਥੀ। ਮੈਂ ਵਿਸਤਾਰ ਨਾਲ ਸਿਹਤ ਵਿਸ਼ਲੇਸ਼ਣ ਪ੍ਰਦਾਨ ਕਰਦਾ ਹਾਂ ਜਿਸ ਵਿੱਚ ਹਾਲਤ ਮੁੱਲਾਂਕਣ, ਇਲਾਜ ਸੁਝਾਅ ਅਤੇ ਪੇਸ਼ੇਵਰ ਮਾਰਗਦਰਸ਼ਨ ਸ਼ਾਮਲ ਹੈ। ਆਪਣੇ ਲੱਛਣ ਸਾਂਝੇ ਕਰੋ ਅਤੇ ਮੈਂ ਤੁਹਾਨੂੰ ਪੂਰਾ ਸਿਹਤ ਵਿਸ਼ਲੇਸ਼ਣ ਦਿਆਂਗਾ! 😊\n\nਯਾਦ ਰੱਖੋ: ਇਹ AI-ਸੰਚਾਲਿਤ ਵਿਸ਼ਲੇਸ਼ਣ ਹੈ। ਅੰਤਿਮ ਨਿਦਾਨ ਅਤੇ ਇਲਾਜ ਲਈ ਹਮੇਸ਼ਾ ਸਿਹਤ ਪੇਸ਼ੇਵਰ ਨਾਲ ਸਲਾਹ ਕਰੋ।",
        
        // Medical Analysis Terms (Punjabi)
        analysisComplete: "ਵਿਸ਼ਲੇਸ਼ਣ ਪੂਰਾ",
        predictedCondition: "ਅਨੁਮਾਨਿਤ ਹਾਲਤ",
        confidence: "ਵਿਸ਼ਵਾਸ",
        detailedMedicalAnalysis: "ਵਿਸਤਾਰ ਨਾਲ ਮੈਡੀਕਲ ਵਿਸ਼ਲੇਸ਼ਣ",
        commonSymptoms: "ਸਾਂਝੇ ਲੱਛਣ",
        recommendedTests: "ਸਿਫਾਰਸ਼ ਕੀਤੇ ਗਏ ਨੈਦਾਨਿਕ ਟੈਸਟ",
        treatmentOptions: "ਇਲਾਜ ਵਿਕਲਪ",
        whenToSeekCare: "ਤੁਰੰਤ ਮੈਡੀਕਲ ਸਹਾਇਤਾ ਕਦੋਂ ਲਓ",
        medicalNote: "ਨੋਟ: ਇਹ ਇੱਕ AI ਭਵਿੱਖਬਾਣੀ ਹੈ। ਸਹੀ ਨਿਦਾਨ ਅਤੇ ਇਲਾਜ ਯੋਜਨਾ ਲਈ ਮੈਡੀਕਲ ਪੇਸ਼ੇਵਰ ਨਾਲ ਸਲਾਹ ਕਰੋ।",
        important: "ਮਹੱਤਵਪੂਰਨ",
        
        // Contact Section
        contactTitle: "ਸੰਪਰਕ ਵਿੱਚ ਰਹੋ",
        contactSubtitle: "ਸਾਰੀਆਂ ਗੈਰ-ਚਿਕਿਤਸਾ ਪੁੱਛਗਿੱਛ ਲਈ, ਕਿਰਪਾ ਕਰਕੇ ਇਹ ਫਾਰਮ ਭਰੋ।",
        namePlaceholder: "ਤੁਹਾਡਾ ਨਾਮ",
        emailPlaceholder: "ਤੁਹਾਡਾ ਈਮੇਲ",
        messagePlaceholder: "ਤੁਹਾਡਾ ਸੰਦੇਸ਼",
        sendMessageButton: "ਸੰਦੇਸ਼ ਭੇਜੋ",
        
        // Footer
        footerText: "© 2024 ਆਰੋਗਿਆਲਿੰਕ। ਸਾਰੇ ਅਧਿਕਾਰ ਸੁਰੱਖਿਤ।",
        privacyPolicy: "ਗੁਪਤਤਾ ਨੀਤੀ",
        termsOfService: "ਸੇਵਾ ਦੀਆਂ ਸ਼ਰਤਾਂ",
        placeholder: "ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੇ ਲੱਛਣਾਂ ਦਾ ਵਿਸਤਾਰ ਨਾਲ ਵਰਣਨ ਕਰੋ... ਉਦਾਹਰਣ ਲਈ: 'ਮੈਨੂੰ ਅੱਜ ਸਵੇਰੇ ਤੋਂ ਬਹੁਤ ਸਿਰ ਦਰਦ ਹੈ। ਇਹ ਧੜਕ ਰਿਹਾ ਹੈ ਅਤੇ ਮੇਰੇ ਸਿਰ ਦੇ ਸੱਜੇ ਪਾਸੇ ਹੈ। ਮੈਨੂੰ ਜੀ ਵੀ ਮਿਚਲਾ ਰਿਹਾ ਹੈ।'",
        quickTip: "ਤੇਜ਼ ਸੁਝਾਅ: ਦੱਸੋ ਕਿ ਇਹ ਕਦੋਂ ਸ਼ੁਰੂ ਹੋਇਆ, ਦਰਦ ਦਾ ਪੱਧਰ (1-10), ਅਤੇ ਕੀ ਇਸਨੂੰ ਬਿਹਤਰ/ਮਾੜਾ ਬਣਾਉਂਦਾ ਹੈ",
        quickStartOptions: "ਤੇਜ਼ ਸ਼ੁਰੂਆਤ ਵਿਕਲਪ:",
        
        // Additional missing translations  
        getStarted: "ਸ਼ੁਰੂ ਕਰੋ",
        quickTip: "ਤੇਜ਼ ਸੁਝਾਅ: ਦੱਸੋ ਕਿ ਇਹ ਕਦੋਂ ਸ਼ੁਰੂ ਹੋਇਆ, ਦਰਦ ਦਾ ਪੱਧਰ (1-10), ਅਤੇ ਕੀ ਇਸਨੂੰ ਬਿਹਤਰ/ਮਾੜਾ ਬਣਾਉਂਦਾ ਹੈ",
        
        // Quick prompt button translations
        headache: "🤕 ਸਿਰ ਦਰਦ",
        fever: "🤒 ਬੁਖਾਰ",
        stomach: "😷 ਪੇਟ ਦਰਦ",
        cough: "😷 ਖੰਘ/ਜ਼ੁਕਾਮ",
        fatigue: "😴 ਥਕਾਵਟ",
        injury: "🤕 ਸੱਟ/ਦਰਦ",
        
        greeting: "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਡਾ. ਆਰੋਗਿਆਲਿੰਕ ਹਾਂ, ਤੁਹਾਡਾ AI ਸਿਹਤ ਸਾਥੀ। ਮੈਂ ਵਿਸਤਾਰ ਨਾਲ ਸਿਹਤ ਵਿਸ਼ਲੇਸ਼ਣ ਪ੍ਰਦਾਨ ਕਰਦਾ ਹੈਂ ਜਿਸ ਵਿੱਚ ਹਾਲਤ ਮੁੱਲਾਂਕਣ, ਇਲਾਜ ਸੁਝਾਅ ਅਤੇ ਪੇਸ਼ੇਵਰ ਮਾਰਗਦਰਸ਼ਨ ਸ਼ਾਮਲ ਹੈ। ਆਪਣੇ ਲੱਛਣ ਸਾਂਝੇ ਕਰੋ ਅਤੇ ਮੈਂ ਤੁਹਾਨੂੰ ਪੂਰਾ ਸਿਹਤ ਵਿਸ਼ਲੇਸ਼ਣ ਦਿਆਂਗਾ! 😊\n\nਯਾਦ ਰੱਖੋ: ਇਹ AI-ਸੰਚਾਲਿਤ ਵਿਸ਼ਲੇਸ਼ਣ ਹੈ। ਅੰਤਿਮ ਨਿਦਾਨ ਅਤੇ ਇਲਾਜ ਲਈ ਹਮੇਸ਼ਾ ਸਿਹਤ ਪੇਸ਼ੇਵਰ ਨਾਲ ਸਲਾਹ ਕਰੋ।",
        name: "ਪੰਜਾਬੀ",
        placeholder: "ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੇ ਲੱਛਣਾਂ ਦਾ ਵਿਸਤਾਰ ਨਾਲ ਵਰਣਨ ਕਰੋ... ਉਦਾਹਰਣ ਲਈ: 'ਮੈਨੂੰ ਅੱਜ ਸਵੇਰੇ ਤੋਂ ਬਹੁਤ ਸਿਰ ਦਰਦ ਹੈ। ਇਹ ਧੜਕ ਰਿਹਾ ਹੈ ਅਤੇ ਮੇਰੇ ਸਿਰ ਦੇ ਸੱਜੇ ਪਾਸੇ ਹੈ। ਮੈਨੂੰ ਜੀ ਵੀ ਮਿਚਲਾ ਰਿਹਾ ਹੈ।'",
        quickPrompts: {
            headache: "🤕 ਸਿਰ ਦਰਦ",
            fever: "🤒 ਬੁਖਾਰ",
            stomach: "😷 ਪੇਟ ਦਰਦ",
            cough: "😷 ਖੰਘ/ਜ਼ੁਕਾਮ",
            fatigue: "😴 ਥਕਾਵਟ",
            injury: "🤕 ਸੱਟ/ਦਰਦ"
        },
        buttons: {
            send: "ਭੇਜੋ",
            record: "ਰਿਕਾਰਡਿੰਗ ਸ਼ੁਰੂ ਕਰੋ",
            analyze: "ਤਸਵੀਰ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰੋ",
            startAI: "AI ਵਿਸ਼ਲੇਸ਼ਣ ਸ਼ੁਰੂ ਕਰੋ"
        }
    }
};

function toggleLanguageDropdown() {
    const dropdown = document.getElementById('languageDropdown');
    
    if (!dropdown) {
        console.warn('Language dropdown element not found');
        return;
    }
    
    isLanguageDropdownOpen = !isLanguageDropdownOpen;
    
    if (isLanguageDropdownOpen) {
        dropdown.classList.add('show');
    } else {
        dropdown.classList.remove('show');
    }
}

function changeLanguage(langCode) {
    if (!translations[langCode]) {
        console.error('Invalid language code:', langCode);
        return;
    }
    
    currentLanguage = langCode;
    const currentLangElement = document.getElementById('currentLanguage');
    
    // Update language display
    if (currentLangElement) {
        currentLangElement.textContent = translations[langCode].name;
    }
    
    // Update active language option - fix the selector
    document.querySelectorAll('.language-option').forEach(option => {
        option.classList.remove('active');
    });
    
    const activeOption = document.querySelector(`.language-option[data-lang="${langCode}"]`);
    if (activeOption) {
        activeOption.classList.add('active');
    }
    
    // Close dropdown
    if (isLanguageDropdownOpen) {
        toggleLanguageDropdown();
    }
    
    // Update UI elements
    updateLanguageContent(langCode);
    
    // Save language preference
    localStorage.setItem('preferredLanguage', langCode);
    
    // Update greeting message
    updateGreetingMessage(langCode);
    
    console.log('Language changed to:', translations[langCode].name);
}

function updateLanguageContent(langCode) {
    const lang = translations[langCode];
    
    if (!lang) {
        console.error('Language not found:', langCode);
        return;
    }
    
    // Update elements with data-translate attributes
    const translatableElements = document.querySelectorAll('[data-translate]');
    translatableElements.forEach(element => {
        const key = element.getAttribute('data-translate');
        if (lang[key]) {
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = lang[key];
            } else {
                element.textContent = lang[key];
            }
        }
    });
    
    // Update elements with data-translate-placeholder attributes
    const placeholderElements = document.querySelectorAll('[data-translate-placeholder]');
    placeholderElements.forEach(element => {
        const key = element.getAttribute('data-translate-placeholder');
        if (lang[key]) {
            element.placeholder = lang[key];
        }
    });
    
    // Update specific elements by ID/class
    const elements = {
        'messageInput': { type: 'placeholder', key: 'placeholder' },
        'imageDescription': { type: 'placeholder', key: 'imageDescPlaceholder' },
        'contactName': { type: 'placeholder', key: 'namePlaceholder' },
        'contactEmail': { type: 'placeholder', key: 'emailPlaceholder' },
        'contactMessage': { type: 'placeholder', key: 'messagePlaceholder' },
        'recordButton': { type: 'text', key: 'startRecordingButton' },
        'themeText': { type: 'text', key: 'themeToggle' }
    };
    
    Object.keys(elements).forEach(id => {
        const element = document.getElementById(id);
        const config = elements[id];
        if (element && lang[config.key]) {
            if (config.type === 'placeholder') {
                element.placeholder = lang[config.key];
            } else {
                element.textContent = lang[config.key];
            }
        }
    });
    
    // Update tab labels
    const tabs = document.querySelectorAll('.tab[data-translate]');
    tabs.forEach(tab => {
        const key = tab.getAttribute('data-translate');
        if (lang[key]) {
            const textSpan = tab.querySelector('span:not(.material-symbols-outlined)');
            if (textSpan) {
                textSpan.textContent = lang[key];
            } else {
                // If no separate span, update the button text while preserving the icon
                const icon = tab.querySelector('.material-symbols-outlined');
                if (icon) {
                    tab.innerHTML = '';
                    tab.appendChild(icon);
                    const textNode = document.createTextNode(lang[key]);
                    tab.appendChild(textNode);
                }
            }
        }
    });
    
    // Update quick prompt buttons
    const quickPromptSelectors = [
        'button[onclick*="setQuickPrompt(\'headache\')"]',
        'button[onclick*="setQuickPrompt(\'fever\')"]',
        'button[onclick*="setQuickPrompt(\'stomach\')"]',
        'button[onclick*="setQuickPrompt(\'cough\')"]',
        'button[onclick*="setQuickPrompt(\'fatigue\')"]',
        'button[onclick*="setQuickPrompt(\'injury\')"]'
    ];
    
    const promptKeys = ['headache', 'fever', 'stomach', 'cough', 'fatigue', 'injury'];
    
    quickPromptSelectors.forEach((selector, index) => {
        const button = document.querySelector(selector);
        const key = promptKeys[index];
        if (button && lang.quickPrompts && lang.quickPrompts[key]) {
            button.textContent = lang.quickPrompts[key];
        }
    });
    
    // Update button texts
    const sendButton = document.querySelector('button[onclick="sendTextMessage()"]');
    if (sendButton && lang.buttons && lang.buttons.send) {
        sendButton.innerHTML = `<span class="material-symbols-outlined">send</span>`;
        sendButton.setAttribute('title', lang.buttons.send);
    }
    
    const recordButton = document.getElementById('recordButton');
    if (recordButton && lang.buttons && lang.buttons.record) {
        recordButton.textContent = lang.buttons.record;
    }
}

function updateGreetingMessage(langCode) {
    const chatContainer = document.getElementById('chatContainer');
    if (!chatContainer) return;
    
    const existingGreeting = chatContainer.querySelector('.message.ai .message-bubble');
    
    if (existingGreeting && translations[langCode]) {
        existingGreeting.innerHTML = formatMessageContent(translations[langCode].greeting);
        
        // Add a subtle animation to indicate language change
        existingGreeting.style.transform = 'scale(0.95)';
        existingGreeting.style.opacity = '0.8';
        
        setTimeout(() => {
            existingGreeting.style.transform = 'scale(1)';
            existingGreeting.style.opacity = '1';
        }, 200);
    }
}

function formatMessageContent(content) {
    // Convert newlines to HTML breaks
    return content.replace(/\n/g, '<br>');
}

function initializeLanguage() {
    // Load saved language preference
    const savedLanguage = localStorage.getItem('preferredLanguage') || 'en';
    
    if (savedLanguage !== 'en') {
        changeLanguage(savedLanguage);
    }
    
    // Set up event listeners
    setupLanguageEventListeners();
}

function setupLanguageEventListeners() {
    // Close dropdown when clicking outside
    document.addEventListener('click', function(event) {
        const languageSwitcher = event.target.closest('.language-switcher');
        
        if (!languageSwitcher && isLanguageDropdownOpen) {
            toggleLanguageDropdown();
        }
    });
    
    // Prevent dropdown from closing when clicking inside
    const dropdown = document.getElementById('languageDropdown');
    if (dropdown) {
        dropdown.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing language system...');
    initializeLanguage();
});

// Export functions for global access
window.toggleLanguageDropdown = toggleLanguageDropdown;
window.changeLanguage = changeLanguage;
window.currentLanguage = () => currentLanguage;