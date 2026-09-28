const translations = {
  en: {
    // Nav
    dashboard:        'Dashboard',
    profile:          'Profile',
    reports:          'Reports',
    prescriptions:    'Prescriptions',
    medicines:        'Medicines',
    reminders:        'Reminders',
    appointments:     'Appointments',
    chatbot:          'AI Assistant',
    locker:           'Medical Locker',
    family:           'Family Profiles',
    emergency:        'Emergency',
    notifications:    'Notifications',
    settings:         'Settings',
    logout:           'Logout',
    // Common
    save:             'Save',
    cancel:           'Cancel',
    submit:           'Submit',
    delete:           'Delete',
    edit:             'Edit',
    view:             'View',
    upload:           'Upload',
    download:         'Download',
    search:           'Search',
    loading:          'Loading...',
    noData:           'No data available',
    // Status
    normal:           'Normal',
    attention:        'Attention',
    abnormal:         'Abnormal',
    // Disclaimer
    aiDisclaimer:     '⚠️ AI-generated information is for educational purposes only. Always consult your doctor.',
    emergencyAlert:   '🚨 This may require urgent medical attention. Call 112 immediately.',
  },
  ta: {
    dashboard:        'டாஷ்போர்டு',
    profile:          'சுயவிவரம்',
    reports:          'அறிக்கைகள்',
    prescriptions:    'மருந்துச்சீட்டுகள்',
    medicines:        'மருந்துகள்',
    reminders:        'நினைவூட்டல்கள்',
    appointments:     'சந்திப்புகள்',
    chatbot:          'AI உதவியாளர்',
    locker:           'மருத்துவ லாக்கர்',
    family:           'குடும்ப சுயவிவரங்கள்',
    emergency:        'அவசரநிலை',
    notifications:    'அறிவிப்புகள்',
    settings:         'அமைப்புகள்',
    logout:           'வெளியேறு',
    save:             'சேமி',
    cancel:           'ரத்து செய்',
    submit:           'சமர்ப்பி',
    delete:           'நீக்கு',
    edit:             'திருத்து',
    view:             'பார்',
    upload:           'பதிவேற்று',
    download:         'பதிவிறக்கு',
    search:           'தேடு',
    loading:          'ஏற்றுகிறது...',
    noData:           'தகவல் இல்லை',
    normal:           'சாதாரண',
    attention:        'கவனம்',
    abnormal:         'அசாதாரண',
    aiDisclaimer:     '⚠️ AI-உருவாக்கிய தகவல் கல்வி நோக்கங்களுக்காக மட்டுமே. எப்போதும் உங்கள் மருத்துவரை அணுகவும்.',
    emergencyAlert:   '🚨 இதற்கு உடனடி மருத்துவ கவனிப்பு தேவைப்படலாம். 112 ஐ உடனே அழைக்கவும்.',
  },
};

export default translations;

export function useTranslation(lang = 'en') {
  const t = translations[lang] || translations.en;
  return (key) => t[key] || key;
}
