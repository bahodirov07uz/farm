# Med Frontend - Farmatsevtika Tizimi

React asosida yozilgan zamonaviy va sodda frontend ilovasi.

## Texnologiyalar

- **React 18** - UI kutubxonasi
- **Vite** - Build tool va dev server
- **React Router** - Routing
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Lucide React** - Ikonlar

## O'rnatish

1. Dependencies o'rnatish:
```bash
cd frontend
npm install
```

2. Development server ishga tushirish:
```bash
npm run dev
```

3. Browserda ochish:
```
http://localhost:3000
```

## Build

Production build yaratish:
```bash
npm run build
```

## API Configuration

Frontend backend API bilan aloqa qiladi. Backend `http://localhost:8000` da ishlashi kerak.

Vite proxy konfiguratsiyasi `vite.config.js` faylida sozlangan.

## Struktura

```
frontend/
├── src/
│   ├── components/     # Reusable komponentlar
│   ├── contexts/       # React Context (Auth)
│   ├── pages/          # Sahifalar
│   ├── services/       # API servislar
│   ├── App.jsx         # Asosiy komponent
│   └── main.jsx        # Entry point
├── index.html
├── package.json
└── vite.config.js
```

## Funksiyalar

- ✅ Foydalanuvchi autentifikatsiyasi (Login/Register)
- ✅ Aptekalar boshqaruvi
- ✅ Filiallar boshqaruvi
- ✅ Dorilar va variantlar boshqaruvi
- ✅ Ombor boshqaruvi
- ✅ Buyurtmalar boshqaruvi
- ✅ Role-based access control
- ✅ Responsive dizayn

## Foydalanish

1. **Ro'yxatdan o'tish**: Yangi foydalanuvchi yaratish
2. **Kirish**: Mavjud hisobga kirish
3. **Dashboard**: Asosiy statistika va ma'lumotlar
4. **Aptekalar**: Aptekalar ro'yxati va so'rovlar
5. **Filiallar**: Filiallar boshqaruvi
6. **Dorilar**: Dorilar va variantlar boshqaruvi
7. **Ombor**: Ombor ma'lumotlari va umumiy miqdorlar
8. **Buyurtmalar**: Buyurtmalar yaratish va boshqarish

## Rol va huquqlar

- **superadmin**: Barcha funksiyalar
- **operator**: Aptekalar, filiallar, dorilar boshqaruvi
- **pharmacy_admin**: O'z aptekasi uchun boshqaruv
- **branch_admin**: O'z filiali uchun boshqaruv
- **cashier**: Buyurtmalar yaratish va tasdiqlash

