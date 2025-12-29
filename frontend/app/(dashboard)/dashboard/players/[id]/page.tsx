'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import ApiClient from '@/lib/api-client'
import { Player } from '@/lib/types/player'

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

// interface PlayerDetailPageProps {
//   params: {
//     id: string
//   }
// }

export default function PlayerDetailPage() {
  const { getToken } = useAuth()
  const params = useParams<{ id: string }>()
  const router = useRouter()
  const [player, setPlayer] = useState<Player | null>(null)
  const [similarPlayers, setSimilarPlayers] = useState<Player[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    fetchPlayerData()
  }, [params.id])

  const fetchPlayerData = async () => {
    try {
      setLoading(true)
      setError(null)

      const token = await getToken()
      const api = new ApiClient(token!)

      // Fetch player details
      const playerResponse = await api.players.get(params.id)
      console.log("playerResponse", playerResponse)
      setPlayer(playerResponse.data.data)

      // Fetch similar players
      try {
        const similarResponse = await api.players.similar(params.id)
        setSimilarPlayers(similarResponse.data.data)
      } catch (err) {
        // Similar players is optional, don't fail the whole page
        console.log('Could not fetch similar players')
      }

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch player')
      console.error('Error fetching player:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    try {
      setDeleting(true)
      const token = await getToken()
      const api = new ApiClient(token!)

      await api.players.delete(params.id)
      router.push('/dashboard/players')
      router.refresh()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete player')
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

  const getPositionColor = (position: string) => {
    const colors: Record<string, string> = {
      'GK': 'bg-yellow-100 text-yellow-800',
      'DF': 'bg-blue-100 text-blue-800',
      'CB': 'bg-blue-100 text-blue-800',
      'LB': 'bg-blue-100 text-blue-800',
      'RB': 'bg-blue-100 text-blue-800',
      'MF': 'bg-green-100 text-green-800',
      'CM': 'bg-green-100 text-green-800',
      'CDM': 'bg-green-100 text-green-800',
      'CAM': 'bg-green-100 text-green-800',
      'FW': 'bg-red-100 text-red-800',
      'ST': 'bg-red-100 text-red-800',
      'CF': 'bg-red-100 text-red-800',
      'LW': 'bg-red-100 text-red-800',
      'RW': 'bg-red-100 text-red-800',
    }
    return colors[position] || 'bg-gray-100 text-gray-800'
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

  if (error || !player) {
    return (
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <Alert variant="destructive">
            <AlertDescription>{error || 'Player not found'}</AlertDescription>
          </Alert>
          <Button
            variant="outline"
            onClick={() => router.push('/dashboard/players')}
            className="mt-4 cursor-pointer"
          >
            ← Back to Players
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
            onClick={() => router.push('/dashboard/players')}
            className="mb-4"
          >
            ← Back to Players
          </Button>
          
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-4xl font-bold">{player.name}</h1>
                <Badge className={getPositionColor(player.position)}>
                  {player.position}
                </Badge>
              </div>
              {player.full_name && player.full_name !== player.name && (
                <p className="text-gray-500 text-lg">{player.full_name}</p>
              )}
              {player.current_club && (
                <p className="text-gray-600 mt-1">
                  <span className="font-semibold">{player.current_club}</span>
                  {player.nationality && ` • ${player.nationality}`}
                </p>
              )}
            </div>

            <div className="flex gap-2">
              <Link href={`/dashboard/players/${player.id}/edit`}>
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
                      This will permanently delete {player.name} from the database.
                      This action cannot be undone.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction
                      onClick={handleDelete}
                      disabled={deleting}
                      className="bg-red-600 hover:bg-red-700"
                    >
                      {deleting ? 'Deleting...' : 'Delete Player'}
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
                        <dd className="text-lg font-semibold">{player.age || 'N/A'}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Date of Birth</dt>
                        <dd className="text-lg font-semibold">{formatDate(player.date_of_birth)}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Nationality</dt>
                        <dd className="text-lg font-semibold">{player.nationality || 'N/A'}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Position</dt>
                        <dd className="text-lg font-semibold">{player.position}</dd>
                      </div>
                    </dl>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Physical Attributes</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <dl className="grid grid-cols-3 gap-4">
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Height</dt>
                        <dd className="text-lg font-semibold">
                          {player.height_cm ? `${player.height_cm} cm` : 'N/A'}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Weight</dt>
                        <dd className="text-lg font-semibold">
                          {player.weight_kg ? `${player.weight_kg} kg` : 'N/A'}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Preferred Foot</dt>
                        <dd className="text-lg font-semibold capitalize">
                          {player.preferred_foot || 'N/A'}
                        </dd>
                      </div>
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
                        <dt className="text-sm font-medium text-gray-500">Market Value</dt>
                        <dd className="text-2xl font-bold text-green-600">
                          {formatCurrency(player.market_value_eur)}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Overall Rating</dt>
                        <dd className="text-2xl font-bold">
                          {player.overall_rating ? (
                            <Badge variant="outline" className="text-lg px-3 py-1">
                              {player.overall_rating}
                            </Badge>
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
                      <div>
                        <div className="flex justify-between mb-2">
                          <dt className="text-sm font-medium">Overall Rating</dt>
                          <dd className="text-sm font-semibold">{player.overall_rating || 'N/A'}</dd>
                        </div>
                        {player.overall_rating && (
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${player.overall_rating}%` }}
                            />
                          </div>
                        )}
                      </div>
                      
                      <div>
                        <div className="flex justify-between mb-2">
                          <dt className="text-sm font-medium">Potential Rating</dt>
                          <dd className="text-sm font-semibold">{player.potential_rating || 'N/A'}</dd>
                        </div>
                        {player.potential_rating && (
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-green-600 h-2 rounded-full"
                              style={{ width: `${player.potential_rating}%` }}
                            />
                          </div>
                        )}
                      </div>
                    </dl>

                    {(!player.overall_rating && !player.potential_rating) && (
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
                    {player.scouting_notes ? (
                      <p className="whitespace-pre-wrap">{player.scouting_notes}</p>
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
                    <dd className="text-sm font-semibold">{player.age || 'N/A'}</dd>
                  </div>
                  <Separator />
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-500">Rating</dt>
                    <dd className="text-sm font-semibold">{player.overall_rating || 'N/A'}</dd>
                  </div>
                  <Separator />
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-500">Potential</dt>
                    <dd className="text-sm font-semibold">{player.potential_rating || 'N/A'}</dd>
                  </div>
                  <Separator />
                  <div className="flex justify-between">
                    <dt className="text-sm text-gray-500">Value</dt>
                    <dd className="text-sm font-semibold">{formatCurrency(player.market_value_eur)}</dd>
                  </div>
                </dl>
              </CardContent>
            </Card>

            {/* Similar Players */}
            {similarPlayers.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Similar Players</CardTitle>
                  <CardDescription>Based on position, age, and value</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {similarPlayers.map((similar) => (
                      <div
                        key={similar.id}
                        className="flex items-center justify-between p-3 rounded-lg border hover:bg-gray-50 cursor-pointer"
                        onClick={() => router.push(`/dashboard/players/${similar.id}`)}
                      >
                        <div>
                          <p className="font-semibold text-sm">{similar.name}</p>
                          <p className="text-xs text-gray-500">
                            {similar.current_club} • {similar.position}
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
                    <dd className="font-medium">{formatDate(player.created_at)}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-500">Player ID</dt>
                    <dd className="font-mono text-xs text-gray-400">{player.id}</dd>
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