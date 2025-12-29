'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import ApiClient from '@/lib/api-client'
import { Coach } from '@/lib/types/coach'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'

// interface CoachDetailPageProps {
//   params: {
//     id: string
//   }
// }

export default function CoachDetailPage() {
  const { getToken } = useAuth()
  const params = useParams<{ id: string }>()
  const router = useRouter()
  const [Coach, setCoach] = useState<Coach | null>(null)
  const [similarCoaches, setSimilarCoaches] = useState<Coach[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    fetchCoachData()
  }, [params.id])

  const fetchCoachData = async () => {
    try {
      setLoading(true)
      setError(null)

      const token = await getToken()
      const api = new ApiClient(token!)

      // Fetch Coach details
      const CoachResponse = await api.coaches.get(params.id)
      console.log("CoachResponse", CoachResponse)
      setCoach(CoachResponse.data.data)

      // Fetch similar Coaches
      try {
        const similarResponse = await api.coaches.similar(params.id)
        setSimilarCoaches(similarResponse.data.data)
      } catch (err) {
        // Similar Coaches is optional, don't fail the whole page
        console.log('Could not fetch similar Coaches')
      }

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch Coach')
      console.error('Error fetching Coach:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    try {
      setDeleting(true)
      const token = await getToken()
      const api = new ApiClient(token!)

      await api.coaches.delete(params.id)
      router.push('/dashboard/coaches')
      router.refresh()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete Coach')
    } finally {
      setDeleting(false)
    }
  }

  const formatCurrency = (value?: number) => {
    if (!value) return 'N/A'
    if (value >= 1000000) return `€${(value / 1000000).toFixed(1)}M`
    if (value >= 1000) return `€${(value / 1000).toFixed(0)}K`
    return `€${value}`
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    })
  }

   const getRoleColor = (current_role: string) => {
    const colors: Record<string, string> = {
      'head_coach': 'bg-purple-100 text-purple-800',
      'assistant': 'bg-blue-100 text-blue-800',
      'youth_coach': 'bg-green-100 text-green-800',
    }
    return colors[current_role] || 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <Skeleton className="h-10 w-48 mb-6" />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Skeleton className="h-96 w-full" />
            </div>
            <div>
              <Skeleton className="h-64 w-full" />
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error || !Coach) {
    return (
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <Alert variant="destructive">
            <AlertDescription>{error || 'Coach not found'}</AlertDescription>
          </Alert>
          <Button
            variant="outline"
            onClick={() => router.push('/dashboard/coaches')}
            className="mt-4 cursor-pointer"
          >
            ← Back to Coaches
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Button
            variant="outline"
            onClick={() => router.push('/dashboard/coaches')}
            className="mb-4 cursor-pointer"
          >
            {`<`} Back to Coaches
          </Button>
          
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-4xl font-bold">{Coach.name}</h1>
                <Badge className={getRoleColor(Coach.current_role)}>
                  {Coach.current_role}
                </Badge>
              </div>
              {Coach.full_name && Coach.full_name !== Coach.name && (
                <p className="text-gray-500 text-lg">{Coach.full_name}</p>
              )}
              {Coach.current_club && (
                <p className="text-gray-600 mt-1">
                  <span className="font-semibold">{Coach.current_club}</span>
                  {Coach.nationality && ` • ${Coach.nationality}`}
                </p>
              )}
            </div>

            <div className="flex gap-2">
              <Link href={`/dashboard/coaches/${Coach.id}/edit`}>
                <Button variant="outline" className='cursor-pointer'>Edit</Button>
              </Link>
              
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="destructive"  className='cursor-pointer'>Delete</Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                    <AlertDialogDescription>
                      This will permanently delete {Coach.name} from the database.
                      This action cannot be undone.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction
                      onClick={handleDelete}
                      disabled={deleting}
                      className="bg-red-600 hover:bg-red-700 cursor-pointer"
                    >
                      {deleting ? 'Deleting...' : 'Delete Coach'}
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="overview" className='cursor-pointer hover:bg-opacity-10'>Overview</TabsTrigger>
                <TabsTrigger value="stats" className='cursor-pointer hover:bg-opacity-10'>Statistics</TabsTrigger>
                <TabsTrigger value="notes" className='cursor-pointer hover:bg-opacity-10'>Scouting Notes</TabsTrigger>
              </TabsList>

              {/* Overview Tab */}
              <TabsContent value="overview" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Basic Information</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <dl className="grid grid-cols-2 gap-4">
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Age</dt>
                        <dd className="text-lg font-semibold">{Coach.age || 'N/A'}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Current Club</dt>
                        <dd className="text-lg font-semibold">{Coach.current_club}</dd>
                        {/* <dd className="text-lg font-semibold">{formatDate(Coach.date_of_birth)}</dd> */}
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Nationality</dt>
                        <dd className="text-lg font-semibold">{Coach.nationality || 'N/A'}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">current_role</dt>
                        <dd className="text-lg font-semibold">{Coach.current_role}</dd>
                      </div>
                    </dl>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Tactical Information</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <dl className="grid grid-cols-3 gap-4">
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Preferred Formation</dt>
                        <dd className="text-lg font-semibold">
                          {Coach.preferred_formation ? `${Coach.preferred_formation}` : 'N/A'}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Coaching Level</dt>
                        <dd className="text-lg font-semibold">
                          {Coach.coaching_level ? `${Coach.coaching_level}` : 'N/A'}
                        </dd>
                      </div>
                      {/* <div>
                        <dt className="text-sm font-medium text-gray-500">Preferred Foot</dt>
                        <dd className="text-lg font-semibold capitalize">
                          {Coach.preferred_foot || 'N/A'}
                        </dd>
                      </div> */}
                    </dl>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Financial Information</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <dl className="grid grid-cols-2 gap-4">
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Estimated Salary</dt>
                        <dd className="text-2xl font-bold text-green-600">
                          {formatCurrency(Coach.estimated_salary_eur)}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Years of Experience</dt>
                        <dd className="text-2xl font-bold">
                          {Coach.years_experience ? (
                             Coach.years_experience
                          ) : (
                            'N/A'
                          )}
                        </dd>
                      </div>
                    </dl>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Statistics Tab */}
              <TabsContent value="stats">
                <Card>
                  <CardHeader>
                    <CardTitle>Performance Ratings</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <dl className="space-y-4">
                      {/* <div>
                        <div className="flex justify-between mb-2">
                          <dt className="text-sm font-medium">Coaching Level</dt>
                          <dd className="text-sm font-semibold">{Coach.coaching_level || 'N/A'}</dd>
                        </div>
                        {Coach.coaching_level && (
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${Coach.coaching_level}%` }}
                            />
                          </div>
                        )}
                      </div> */}
                      
                      <div>
                        <div className="flex justify-between mb-2">
                          <dt className="text-sm font-medium">Overall rating</dt>
                          <dd className="text-sm font-semibold">
                            {
                              Coach.overall_rating ?
                            (<Badge variant="outline" className="text-lg px-3 py-1">
                                {Coach.overall_rating}
                            </Badge>)
                             : 'N/A'}</dd>
                            
                        </div>
                        {Coach.overall_rating && (
                          <div className="w-full bg-gray-200 rounded-full h-2">
 
                            <div
                              className="bg-green-600 h-2 rounded-full"
                              style={{ width: `${Coach.overall_rating}%` }}
                            />
                          </div>
                        )}
                      </div>
                    </dl>

                    {!Coach.coaching_level && Coach.overall_rating && (
                      <p className="text-gray-500 text-center py-8">
                        No rating data available
                      </p>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Scouting Notes Tab */}
              <TabsContent value="notes">
                <Card>
                  <CardHeader>
                    <CardTitle>Scouting Notes</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {Coach.scouting_notes ? (
                      <p className="whitespace-pre-wrap">{Coach.scouting_notes}</p>
                    ) : (
                      <p className="text-gray-500 text-center py-8">
                        No scouting notes available
                      </p>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Stats</CardTitle>
              </CardHeader>
              <CardContent>
                <dl className="space-y-3">
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-500">Age</dt>
                    <dd className="text-sm font-semibold">{Coach.age || 'N/A'}</dd>
                  </div>
                  <Separator />
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-500">Rating</dt>
                    <dd className="text-sm font-semibold">{Coach.overall_rating || 'N/A'}</dd>
                  </div>
                  <Separator />
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-500">Coaching Level</dt>
                    <dd className="text-sm font-semibold">{Coach.coaching_level || 'N/A'}</dd>
                  </div>
                  <Separator />
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-500">Value</dt>
                    <dd className="text-sm font-semibold">{formatCurrency(Coach.estimated_salary_eur)}</dd>
                  </div>
                </dl>
              </CardContent>
            </Card>

            {/* Similar Coaches */}
            {similarCoaches.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Similar Coaches</CardTitle>
                  <CardDescription>Based on current_role, age, and value</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {similarCoaches.map((similar) => (
                      <div
                        key={similar.id}
                        className="flex items-center justify-between p-3 rounded-lg border hover:bg-gray-50 cursor-pointer"
                        onClick={() => router.push(`/dashboard/coaches/${similar.id}`)}
                      >
                        <div>
                          <p className="font-semibold text-sm">{similar.name}</p>
                          <p className="text-xs text-gray-500">
                            {similar.current_club} • {similar.current_role}
                          </p>
                        </div>
                        <Badge variant="outline">{similar.overall_rating || 'N/A'}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Metadata */}
            <Card>
              <CardHeader>
                <CardTitle>Metadata</CardTitle>
              </CardHeader>
              <CardContent>
                <dl className="space-y-2 text-sm">
                  <div>
                    <dt className="text-gray-500">Added on</dt>
                    <dd className="font-medium">{formatDate(Coach.created_at)}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-500">Coach ID</dt>
                    <dd className="font-mono text-xs text-gray-400">{Coach.id}</dd>
                  </div>
                </dl>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}