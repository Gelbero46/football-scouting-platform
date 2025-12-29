import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-blue-50 to-white p-24">
      <div className="text-center">
        <h1 className="text-6xl font-bold tracking-tight">
          Football Scouting Platform
        </h1>
        <p className="mt-6 text-xl text-gray-600 max-w-2xl">
          Professional scouting and recruitment platform for football clubs.
          Discover players, analyze performance, and build your dream team.
        </p>
        <div className="mt-10 flex gap-4 justify-center">
          <Link href="/sign-in" className="cursor-pointer">
            <Button size="lg" variant="default">
              Sign In
            </Button>
          </Link>
          <Link href="/sign-up" className='cursor-pointer'>
            <Button size="lg" variant="outline">
              Get Started
            </Button>
          </Link>
        </div>
      </div>
    </main>
  )
}