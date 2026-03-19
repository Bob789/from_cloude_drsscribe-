import Link from 'next/link'

export default function FeaturesPage() {
  const features = [
    {
      icon: '🎤',
      title: 'תמלול אוטומטי',
      description: 'תמלול מדויק עם Whisper AI',
      href: '/product',
    },
    {
      icon: '📝',
      title: 'סיכום חכם',
      description: 'יצירת סיכומים עם OpenAI GPT-4.1',
      href: '/product',
    },
    {
      icon: '🔍',
      title: 'חיפוש מתקדם',
      description: 'חיפוש במטופלים וביקורים',
      href: '/product',
    },
  ]

  return (
    <main className="container mx-auto px-4 py-16">
      <h1 className="text-4xl font-bold text-gray-900 text-center mb-12">
        מערכת התמלול הרפואית
      </h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
        {features.map((feature) => (
          <Link
            key={feature.title}
            href={feature.href}
            className="bg-white rounded-2xl shadow-md p-8 text-center hover:shadow-xl hover:scale-105 transition-all cursor-pointer"
          >
            <div className="text-5xl mb-4">{feature.icon}</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">{feature.title}</h3>
            <p className="text-gray-600">{feature.description}</p>
          </Link>
        ))}
      </div>
    </main>
  )
}
