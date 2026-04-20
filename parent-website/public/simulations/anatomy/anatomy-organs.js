// Organs with 3D-feel SVG and anatomical positions
window.ORGANS = [
  {
    key: 'brain', num: 1, name: 'מוח', nameEn: 'Brain',
    role: 'מרכז הבקרה הראשי',
    desc: 'המוח הוא מרכז הבקרה של הגוף. הוא שולט בכל פעולה <strong>מרצון ושאינה מרצון</strong>: חשיבה, זיכרון, תנועה, נשימה, קצב לב, רגש ותחושה. כל המידע מהחושים מגיע אליו, ומשם יוצאות פקודות לכל הגוף.',
    facts: ['86 מיליארד תאי עצב (נוירונים)', 'צורך 20% מחמצן הגוף', 'משקל כ-1.4 ק״ג', 'מחולק ל-4 אונות עיקריות'],
    stats: [['86B', 'נוירונים'], ['1.4kg', 'משקל'], ['20%', 'חמצן'], ['4', 'אונות']],
    x: 178, y: 20, w: 64, h: 70, // position inside body
    svg: `<svg width="64" height="70" viewBox="0 0 80 80">
      <defs>
        <radialGradient id="brainG" cx="35%" cy="30%">
          <stop offset="0%" stop-color="#f4c7a4"/>
          <stop offset="50%" stop-color="#d08b6b"/>
          <stop offset="100%" stop-color="#6b3a24"/>
        </radialGradient>
      </defs>
      <path d="M40,8 C22,8 10,22 12,38 C8,44 10,56 20,60 C22,68 32,74 40,72 C48,74 58,68 60,60 C70,56 72,44 68,38 C70,22 58,8 40,8 Z"
            fill="url(#brainG)" stroke="#4a2414" stroke-width="1.2"/>
      <path d="M40,14 Q40,40 40,70" stroke="#4a2414" stroke-width="1" fill="none" opacity="0.5"/>
      <path d="M20,30 Q30,28 32,34 Q28,38 22,38" stroke="#4a2414" stroke-width="0.8" fill="none" opacity="0.6"/>
      <path d="M60,30 Q50,28 48,34 Q52,38 58,38" stroke="#4a2414" stroke-width="0.8" fill="none" opacity="0.6"/>
      <path d="M16,48 Q26,46 30,52 Q26,56 20,56" stroke="#4a2414" stroke-width="0.8" fill="none" opacity="0.6"/>
      <path d="M64,48 Q54,46 50,52 Q54,56 60,56" stroke="#4a2414" stroke-width="0.8" fill="none" opacity="0.6"/>
      <ellipse cx="30" cy="22" rx="10" ry="5" fill="rgba(255,255,255,0.3)"/>
    </svg>`
  },
  {
    key: 'heart', num: 2, name: 'לב', nameEn: 'Heart',
    role: 'המשאבה המרכזית',
    desc: 'הלב הוא שריר בגודל אגרוף שפועם <strong>100,000 פעם ביום</strong>. הוא שואב דם עשיר בחמצן לכל הגוף ומחזיר דם דל-חמצן לריאות. מחולק ל-4 חדרים.',
    facts: ['פועם ~100,000 פעמים ביום', 'שואב 7,000 ליטר דם ביממה', '4 חדרי לב', 'נשמע מגיל 6 שבועות ברחם'],
    stats: [['70', 'פעימות/ד׳'], ['5L', 'דם/דקה'], ['300g', 'משקל'], ['4', 'חדרים']],
    x: 175, y: 175, w: 70, h: 80,
    svg: `<svg width="70" height="80" viewBox="0 0 80 90">
      <defs>
        <radialGradient id="heartG2" cx="35%" cy="30%">
          <stop offset="0%" stop-color="#ff7a85"/>
          <stop offset="45%" stop-color="#d6243a"/>
          <stop offset="100%" stop-color="#7a1118"/>
        </radialGradient>
      </defs>
      <path d="M40,82 C12,60 4,40 18,22 C30,10 44,14 48,24 C52,14 66,10 78,22 C88,40 74,60 42,82 L40,82 Z"
            fill="url(#heartG2)" stroke="#5a0f14" stroke-width="1.5"/>
      <ellipse cx="26" cy="30" rx="10" ry="6" fill="rgba(255,255,255,0.35)"/>
      <path d="M40,30 Q35,50 32,68" stroke="#5a0f14" stroke-width="1.5" fill="none" opacity="0.55"/>
      <path d="M40,30 Q45,50 48,68" stroke="#5a0f14" stroke-width="1.5" fill="none" opacity="0.55"/>
      <path d="M40,8 Q42,16 40,24" fill="none" stroke="#9b1a24" stroke-width="4" stroke-linecap="round"/>
    </svg>`
  },
  {
    key: 'lungs-l', num: 3, name: 'ריאה שמאל', nameEn: 'Left Lung',
    role: 'חילוף חמצן',
    desc: 'הריאה השמאלית <strong>קטנה מהימנית</strong> כדי לפנות מקום ללב. מכילה 2 אונות (הימנית 3). אוויר נשאף נכנס לאלבאולי הזעירים, שם החמצן עובר לדם והפחמן הדו-חמצני יוצא.',
    facts: ['2 אונות (הימנית 3)', '300 מיליון אלבאולי', 'שטח חילוף ~70 מ״ר', 'מקבלת דם מחדר ימני של הלב'],
    stats: [['2', 'אונות'], ['300M', 'אלבאולי'], ['16', 'נשימות/ד׳'], ['3L', 'קיבולת']],
    x: 95, y: 160, w: 75, h: 110,
    svg: `<svg width="75" height="110" viewBox="0 0 80 120">
      <defs>
        <radialGradient id="lungLG" cx="30%" cy="25%">
          <stop offset="0%" stop-color="#fdd1db"/>
          <stop offset="50%" stop-color="#e88499"/>
          <stop offset="100%" stop-color="#8a3848"/>
        </radialGradient>
      </defs>
      <path d="M 62,10 Q 75,15 75,50 Q 78,80 70,108 Q 55,115 40,108 Q 30,90 30,70 Q 28,40 38,20 Q 50,8 62,10 Z"
            fill="url(#lungLG)" stroke="#6a2838" stroke-width="1.3"/>
      <ellipse cx="50" cy="30" rx="10" ry="6" fill="rgba(255,255,255,0.3)"/>
      <path d="M 55,18 Q 52,40 48,70 Q 45,95 45,105" stroke="#6a2838" stroke-width="1.2" fill="none" opacity="0.5"/>
      <path d="M 55,18 Q 60,35 62,55" stroke="#6a2838" stroke-width="0.8" fill="none" opacity="0.4"/>
      <path d="M 48,70 Q 58,75 65,80" stroke="#6a2838" stroke-width="0.8" fill="none" opacity="0.4"/>
    </svg>`
  },
  {
    key: 'lungs-r', num: 4, name: 'ריאה ימין', nameEn: 'Right Lung',
    role: 'חילוף חמצן',
    desc: 'הריאה הימנית <strong>גדולה ורחבה יותר</strong> מהשמאלית ומכילה 3 אונות. דרך האלבאולי (שקיקי אוויר) מתבצע חילוף גזים — החמצן עובר לדם ופחמן דו-חמצני משתחרר.',
    facts: ['3 אונות', 'גדולה יותר מהשמאלית', 'מחליפה 10,000 ליטר אוויר ביום', 'מוגנת ע״י כלוב הצלעות'],
    stats: [['3', 'אונות'], ['300M', 'אלבאולי'], ['10K', 'ל׳/יום'], ['3.5L', 'קיבולת']],
    x: 250, y: 160, w: 75, h: 110,
    svg: `<svg width="75" height="110" viewBox="0 0 80 120">
      <defs>
        <radialGradient id="lungRG" cx="70%" cy="25%">
          <stop offset="0%" stop-color="#fdd1db"/>
          <stop offset="50%" stop-color="#e88499"/>
          <stop offset="100%" stop-color="#8a3848"/>
        </radialGradient>
      </defs>
      <path d="M 18,10 Q 5,15 5,50 Q 2,80 10,108 Q 25,115 40,108 Q 50,90 50,70 Q 52,40 42,20 Q 30,8 18,10 Z"
            fill="url(#lungRG)" stroke="#6a2838" stroke-width="1.3"/>
      <ellipse cx="30" cy="30" rx="10" ry="6" fill="rgba(255,255,255,0.3)"/>
      <path d="M 25,18 Q 28,40 32,70 Q 35,95 35,105" stroke="#6a2838" stroke-width="1.2" fill="none" opacity="0.5"/>
      <path d="M 25,18 Q 20,35 18,55" stroke="#6a2838" stroke-width="0.8" fill="none" opacity="0.4"/>
      <path d="M 32,70 Q 22,75 15,80" stroke="#6a2838" stroke-width="0.8" fill="none" opacity="0.4"/>
    </svg>`
  },
  {
    key: 'liver', num: 5, name: 'כבד', nameEn: 'Liver',
    role: 'בית חרושת כימי',
    desc: 'הכבד הוא <strong>האיבר הפנימי הגדול ביותר</strong>. מבצע 500+ תפקידים: מסנן רעלים, מפרק תרופות, מייצר מרה, אוגר סוכר ומייצר חלבוני קרישה. יכול להתחדש מ-25% בלבד.',
    facts: ['500+ תפקידים שונים', 'מפרק אלכוהול ותרופות', 'מייצר מרה לעיכול שומנים', 'מתחדש מ-25% מהמסה'],
    stats: [['1.5kg', 'משקל'], ['500+', 'תפקידים'], ['1.5L', 'דם/ד׳'], ['25%', 'התחדשות']],
    x: 230, y: 275, w: 115, h: 75,
    svg: `<svg width="115" height="75" viewBox="0 0 120 80">
      <defs>
        <radialGradient id="liverG" cx="35%" cy="30%">
          <stop offset="0%" stop-color="#c85a3a"/>
          <stop offset="50%" stop-color="#8a3220"/>
          <stop offset="100%" stop-color="#3e1a15"/>
        </radialGradient>
      </defs>
      <path d="M 10,25 Q 8,12 28,10 L 100,14 Q 115,16 112,38 Q 108,58 95,66 L 40,70 Q 18,68 12,55 Q 6,40 10,25 Z"
            fill="url(#liverG)" stroke="#3e1a15" stroke-width="1.4"/>
      <ellipse cx="38" cy="24" rx="15" ry="6" fill="rgba(255,255,255,0.25)"/>
      <path d="M 60,12 Q 58,40 62,68" stroke="#3e1a15" stroke-width="1" fill="none" opacity="0.5"/>
      <path d="M 30,20 Q 50,35 85,25" stroke="#3e1a15" stroke-width="0.8" fill="none" opacity="0.4"/>
    </svg>`
  },
  {
    key: 'stomach', num: 6, name: 'קיבה', nameEn: 'Stomach',
    role: 'עיכול ראשוני',
    desc: 'הקיבה שק שרירי שמעכל אוכל בעזרת <strong>חומצה הידרוכלורית</strong> (pH 1-2) וחלבונים מפרקים. היא מערבבת את המזון לנוזל סמיך (chyme) ומעבירה למעי הדק.',
    facts: ['חומצה חזקה (pH 1-2)', 'מכילה 1-1.5 ליטר', 'מחדשת רירית כל 3-4 ימים', 'מוחזק 4 שעות לפני מעבר למעי'],
    stats: [['1.5L', 'נפח'], ['pH1-2', 'חומציות'], ['4h', 'זמן שהייה'], ['3-4d', 'התחדשות']],
    x: 125, y: 290, w: 90, h: 75,
    svg: `<svg width="90" height="75" viewBox="0 0 90 80">
      <defs>
        <radialGradient id="stomachG" cx="35%" cy="30%">
          <stop offset="0%" stop-color="#f4a88c"/>
          <stop offset="50%" stop-color="#d06246"/>
          <stop offset="100%" stop-color="#5a2818"/>
        </radialGradient>
      </defs>
      <path d="M 15,15 Q 10,8 30,8 L 55,10 Q 80,20 82,45 Q 78,68 55,72 Q 30,75 20,60 Q 10,40 15,15 Z"
            fill="url(#stomachG)" stroke="#5a2818" stroke-width="1.3"/>
      <ellipse cx="35" cy="22" rx="12" ry="5" fill="rgba(255,255,255,0.3)"/>
      <path d="M 20,30 Q 40,42 70,40" stroke="#5a2818" stroke-width="0.8" fill="none" opacity="0.5"/>
      <path d="M 20,45 Q 40,55 70,55" stroke="#5a2818" stroke-width="0.8" fill="none" opacity="0.4"/>
      <!-- inlet -->
      <path d="M 30,8 Q 28,2 35,2" fill="none" stroke="#d06246" stroke-width="5" stroke-linecap="round"/>
    </svg>`
  },
  {
    key: 'intestine', num: 7, name: 'מעי', nameEn: 'Intestine',
    role: 'ספיגת חומרי מזון',
    desc: 'המעי הדק <strong>באורך 6-7 מטר</strong> סופג את רוב חומרי המזון. המעי הגס קצר יותר (1.5 מטר) אבל רחב, ותפקידו לספוג מים ולגבש צואה. ביחד — מסלול של 8 מטר!',
    facts: ['מעי דק: 6-7 מטר', 'מעי גס: 1.5 מטר', 'שטח ספיגה ~ 250 מ״ר', 'מכיל טריליון חיידקים מועילים'],
    stats: [['8m', 'אורך כולל'], ['250m²', 'שטח ספיגה'], ['1T', 'חיידקים'], ['16h', 'זמן מעבר']],
    x: 130, y: 370, w: 160, h: 140,
    svg: `<svg width="160" height="140" viewBox="0 0 160 140">
      <defs>
        <radialGradient id="intG" cx="40%" cy="30%">
          <stop offset="0%" stop-color="#eab898"/>
          <stop offset="50%" stop-color="#b07050"/>
          <stop offset="100%" stop-color="#5a2f1c"/>
        </radialGradient>
      </defs>
      <!-- Large intestine frame -->
      <path d="M 20,30 Q 18,10 40,12 L 120,12 Q 142,12 140,35 L 140,110 Q 138,128 120,130 L 40,130 Q 20,128 20,110 Z"
            fill="none" stroke="url(#intG)" stroke-width="16" stroke-linecap="round"/>
      <!-- Small intestine coils inside -->
      <path d="M 40,50 Q 55,45 70,55 Q 85,65 70,75 Q 55,85 70,95 Q 90,100 105,90 Q 120,80 105,70 Q 90,60 105,50"
            fill="none" stroke="url(#intG)" stroke-width="10" stroke-linecap="round" opacity="0.9"/>
      <path d="M 50,100 Q 65,95 80,105 Q 95,110 110,102"
            fill="none" stroke="url(#intG)" stroke-width="8" stroke-linecap="round" opacity="0.8"/>
    </svg>`
  },
  {
    key: 'kidney-l', num: 8, name: 'כליה שמאל', nameEn: 'Left Kidney',
    role: 'סינון ופסולת',
    desc: 'הכליה השמאלית מסננת <strong>90 ליטר דם ביום</strong>. היא מייצרת שתן, מווסתת לחץ דם (הורמון רנין), מאזנת מלחים ומפעילה את ייצור כדוריות הדם האדומות (EPO).',
    facts: ['מסננת 90 ליטר ליום', '~1 מיליון נפרונים', 'ממוקמת מאחורי הקיבה', 'מייצרת הורמון EPO'],
    stats: [['90L', 'סינון/יום'], ['1M', 'נפרונים'], ['150g', 'משקל'], ['0.75L', 'שתן/יום']],
    x: 105, y: 360, w: 45, h: 70,
    svg: `<svg width="45" height="70" viewBox="0 0 50 75">
      <defs>
        <radialGradient id="kidLG" cx="30%" cy="25%">
          <stop offset="0%" stop-color="#c09cd2"/>
          <stop offset="50%" stop-color="#7a4a8a"/>
          <stop offset="100%" stop-color="#35203e"/>
        </radialGradient>
      </defs>
      <path d="M 25,5 Q 45,8 45,30 Q 48,55 30,68 Q 10,68 8,50 Q 5,25 15,10 Q 20,5 25,5 Z"
            fill="url(#kidLG)" stroke="#35203e" stroke-width="1.3"/>
      <ellipse cx="20" cy="18" rx="7" ry="4" fill="rgba(255,255,255,0.3)"/>
      <path d="M 38,35 Q 30,38 28,45 Q 30,50 36,48" stroke="#35203e" stroke-width="1" fill="none" opacity="0.6"/>
    </svg>`
  },
  {
    key: 'kidney-r', num: 9, name: 'כליה ימין', nameEn: 'Right Kidney',
    role: 'סינון ופסולת',
    desc: 'הכליה הימנית <strong>ממוקמת מעט נמוך יותר</strong> מהשמאלית בגלל מיקום הכבד. תפקידיה זהים: סינון דם, איזון נוזלים ומלחים, וויסות לחץ דם. הדם עובר בה 25 פעמים ביום.',
    facts: ['נמוכה מעט מהשמאלית', 'הדם עובר ~25 פעם ביום', 'פעילה מאוד בוויסות pH', 'אפשר לחיות עם כליה אחת'],
    stats: [['90L', 'סינון/יום'], ['25x', 'דם/יום'], ['150g', 'משקל'], ['0.75L', 'שתן/יום']],
    x: 270, y: 370, w: 45, h: 70,
    svg: `<svg width="45" height="70" viewBox="0 0 50 75">
      <defs>
        <radialGradient id="kidRG" cx="70%" cy="25%">
          <stop offset="0%" stop-color="#c09cd2"/>
          <stop offset="50%" stop-color="#7a4a8a"/>
          <stop offset="100%" stop-color="#35203e"/>
        </radialGradient>
      </defs>
      <path d="M 25,5 Q 5,8 5,30 Q 2,55 20,68 Q 40,68 42,50 Q 45,25 35,10 Q 30,5 25,5 Z"
            fill="url(#kidRG)" stroke="#35203e" stroke-width="1.3"/>
      <ellipse cx="30" cy="18" rx="7" ry="4" fill="rgba(255,255,255,0.3)"/>
      <path d="M 12,35 Q 20,38 22,45 Q 20,50 14,48" stroke="#35203e" stroke-width="1" fill="none" opacity="0.6"/>
    </svg>`
  },
  {
    key: 'bladder', num: 10, name: 'שלפוחית שתן', nameEn: 'Bladder',
    role: 'אחסון שתן',
    desc: 'שלפוחית השתן היא <strong>שק שרירי גמיש</strong> שאוגר שתן עד להשתנה. יכולה להכיל 400-600 מ״ל. כאשר מתמלאת ב-150-200 מ״ל — מתחילה התחושה של "צריך".',
    facts: ['מכילה 400-600 מ״ל', 'תחושה מופיעה ב-150-200 מ״ל', 'שרירים משתחררים במתן שתן', 'חיידקים = דלקת (UTI)'],
    stats: [['600ml', 'קיבולת'], ['200ml', 'סף תחושה'], ['8x', 'ביום'], ['1.5L', 'ביום']],
    x: 180, y: 495, w: 60, h: 50,
    svg: `<svg width="60" height="50" viewBox="0 0 60 55">
      <defs>
        <radialGradient id="bladG" cx="35%" cy="30%">
          <stop offset="0%" stop-color="#fde8a0"/>
          <stop offset="50%" stop-color="#e8b03a"/>
          <stop offset="100%" stop-color="#7a5010"/>
        </radialGradient>
      </defs>
      <path d="M 10,20 Q 8,5 30,5 Q 52,5 50,20 Q 55,42 30,48 Q 5,42 10,20 Z"
            fill="url(#bladG)" stroke="#5a3a10" stroke-width="1.3"/>
      <ellipse cx="22" cy="18" rx="8" ry="4" fill="rgba(255,255,255,0.35)"/>
      <path d="M 25,5 Q 25,0 30,0" stroke="#7a5010" stroke-width="3" stroke-linecap="round" fill="none"/>
      <path d="M 35,5 Q 35,0 40,0" stroke="#7a5010" stroke-width="3" stroke-linecap="round" fill="none"/>
    </svg>`
  }
];

// Simulation text per organ (shown during "simulate")
window.ORGAN_SIM = {
  heart: 'הלב פועם! בכל דקה שואב כ-5 ליטר דם.',
  brain: 'נוירונים יורים! מעבד מיליארדי אותות בשנייה.',
  'lungs-l': 'ריאה מתמלאת באוויר ומתכווצת — חילוף חמצן פעיל!',
  'lungs-r': 'ריאה מתמלאת באוויר ומתכווצת — חילוף חמצן פעיל!',
  stomach: 'תנועות פריסטלטיקה! הקיבה מערבבת ומעכלת אוכל.',
  intestine: 'גלי עיכול עוברים במעי — סופגים חומרי מזון.',
  liver: 'הכבד עובד! מסנן רעלים ומייצר מרה.',
  'kidney-l': 'הכליה מסננת דם ומייצרת שתן.',
  'kidney-r': 'הכליה מסננת דם ומייצרת שתן.',
  bladder: 'השלפוחית מתרחבת בהדרגה עם שתן נוסף.'
};
