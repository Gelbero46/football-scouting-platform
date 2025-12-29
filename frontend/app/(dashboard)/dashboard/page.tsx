'use client'

import { useAuth, useUser } from '@clerk/nextjs'
import { useEffect, useState } from 'react'
import ApiClient from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function DashboardPage() {
  const { user, isLoaded } = useUser()
  const { getToken } = useAuth()
  const [backendUser, setBackendUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)




  console.log("started----------")
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        // This will trigger user creation in backend if first login
        console.log("okay")
        const token = await getToken()
        if (token) {
          const api = new ApiClient(token)
          const response = await api.auth.getCurrentUser()
          console.log("response", response)
          setBackendUser(response.data.data)
        }
        else {
          setError('No Token Fetched!!')
        }
      
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load user data')
      } finally {
        setLoading(false)
      }
    }

    if (isLoaded && user) {
      fetchUserData()
    }
  }, [isLoaded, user])

  if (!isLoaded || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Error</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Dashboard</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Clerk User Info</CardTitle>
              <CardDescription>Authentication details from Clerk</CardDescription>
            </CardHeader>
            <CardContent>
              <dl className="space-y-2">
                <div>
                  <dt className="font-semibold">Name:</dt>
                  <dd>{user?.firstName} {user?.lastName}</dd>
                </div>
                <div>
                  <dt className="font-semibold">Email:</dt>
                  <dd>{user?.emailAddresses[0]?.emailAddress}</dd>
                </div>
                <div>
                  <dt className="font-semibold">Clerk ID:</dt>
                  <dd className="text-xs text-gray-500">{user?.id}</dd>
                </div>
              </dl>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Backend User Info</CardTitle>
              <CardDescription>User details from your FastAPI backend</CardDescription>
            </CardHeader>
            <CardContent>
              {backendUser ? (
                <dl className="space-y-2">
                  <div>
                    <dt className="font-semibold">Role:</dt>
                    <dd className="capitalize">{backendUser.role}</dd>
                  </div>
                  <div>
                    <dt className="font-semibold">Status:</dt>
                    <dd>{backendUser.is_active ? 'Active' : 'Inactive'}</dd>
                  </div>
                  <div>
                    <dt className="font-semibold">Database ID:</dt>
                    <dd className="text-xs text-gray-500">{backendUser.id}</dd>
                  </div>
                  <div>
                    <dt className="font-semibold">Created:</dt>
                    <dd className="text-sm">{new Date(backendUser.created_at).toLocaleDateString()}</dd>
                  </div>
                </dl>
              ) : (
                <p className="text-gray-500">Loading backend data...</p>
              )}
            </CardContent>
          </Card>
        </div>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Authentication Test</CardTitle>
            <CardDescription>
              This page is protected and only accessible to authenticated users
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-green-600 font-semibold mb-4">
              ✓ Authentication is working! You're seeing this because:
            </p>
            <ul className="list-disc list-inside space-y-2 text-sm">
              <li>You successfully logged in through Clerk</li>
              <li>Clerk issued you a JWT token</li>
              <li>The middleware protected this route</li>
              <li>Your frontend sent the token to the backend</li>
              <li>The backend verified the token and fetched your user data</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}