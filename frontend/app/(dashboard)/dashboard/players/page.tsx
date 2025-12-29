'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import ApiClient from '@/lib/api-client'
import { Player, PlayerFilters, PaginationMeta } from '@/lib/types/player'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export default function PlayersPage() {
  const { getToken } = useAuth()
  const router = useRouter()
  
  const [players, setPlayers] = useState<Player[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pagination, setPagination] = useState<PaginationMeta>({
    page: 1,
    per_page: 20,
    total: 0,
    total_pages: 0
  })
  
  
const [page, setPage] = useState(1)
const [perPage] = useState(20)
// Filters
const [filters, setFilters] = useState<PlayerFilters>({
  search: '',
  position: '',
  club: '',
  sort_by: 'name',
  sort_order: 'asc'
})

  const fetchPlayers = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const token = await getToken()
      const api = new ApiClient(token!)
      
      // Build query params
      const params = {
        skip: (pagination.page - 1) * pagination.per_page,
        limit: pagination.per_page,
        ...(filters.search?.trim() && { search: filters.search.trim() }),
        ...(filters.position && filters.position != "*" && { position: filters.position }),
        ...(filters.club?.trim() && { club: filters.club.trim() }),
        sort_by: filters.sort_by,
        sort_order: filters.sort_order
      }
      
      console.log("params", params)
      const response = await api.players.list(params)
      
      setPlayers(response.data.data)
      setPagination(response.data.meta.pagination)
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch players')
      console.error('Error fetching players:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPlayers()
  }, [pagination.page, filters.sort_order])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    console.log("filters", filters)
    setPagination((prev: PaginationMeta) => ({ ...prev, page: 1 })) // Reset to page 1
    fetchPlayers()
  }

  const handleFilterChange = (key: keyof PlayerFilters, value: string) => {
    setFilters((prev: PlayerFilters) => ({ ...prev, [key]: value }))
  }

  const formatCurrency = (value?: number) => {
    if (!value) return 'N/A'
    if (value >= 1000000) return `€${(value / 1000000).toFixed(1)}M`
    if (value >= 1000) return `€${(value / 1000).toFixed(0)}K`
    return `€${value}`
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

  if (loading && players.length === 0) {
    return (
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <Skeleton className="h-10 w-48 mb-6" />
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold">Players</h1>
            <p className="text-gray-500 mt-1">
              {pagination.total} players in database
            </p>
          </div>
          <Link href="/dashboard/players/new">
            <Button className="cursor-pointer">Add Player</Button>
          </Link>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Filters</CardTitle>
            <CardDescription>Search and filter players</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSearch} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Search */}
                <div className="md:col-span-2">
                  <Input
                    placeholder="Search by name or club..."
                    value={filters.search}
                    onChange={(e) => handleFilterChange('search', e.target.value)}
                  />
                </div>

                {/* Position Filter */}
                <div className="justify-center text-center c">
                     <Select
                      value={filters.position}
                      onValueChange={(value: any) => handleFilterChange('position', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Position" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="*">All Positions</SelectItem>
                        <SelectItem value="GK">Goalkeeper</SelectItem>
                        <SelectItem value="DF">Defender</SelectItem>
                        <SelectItem value="MF">Midfielder</SelectItem>
                        <SelectItem value="FW">Forward</SelectItem>
                        <SelectItem value="ST">Striker</SelectItem>
                        <SelectItem value="LW">Left Wing</SelectItem>
                        <SelectItem value="RW">Right Wing</SelectItem>
                      </SelectContent>
                    </Select>
                </div>
               

                {/* Sort By */}
                <Select
                  value={filters.sort_by}
                  onValueChange={(value: any) => handleFilterChange('sort_by', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Sort by" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="name">Name</SelectItem>
                    <SelectItem value="overall_rating">Rating</SelectItem>
                    <SelectItem value="market_value_eur">Market Value</SelectItem>
                    <SelectItem value="created_at">Date Added</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex gap-2">
                <Button type="submit" disabled={loading} className='cursor-pointer'>
                  {loading ? 'Searching...' : 'Search'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  className='cursor-pointer'
                  onClick={() => {
                    setFilters({
                      search: '',
                      position: '',
                      club: '',
                      sort_by: 'name',
                      sort_order: 'asc'
                    })
                    fetchPlayers()
                  }}
                >
                  Clear
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Players Table */}
        <Card>
          <CardHeader>
            <CardTitle>All Players</CardTitle>
            <CardDescription>
              Click on a player to view details
            </CardDescription>
          </CardHeader>
          <CardContent>
            {players.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No players found</p>
                <p className="text-gray-400 text-sm mt-2">
                  Try adjusting your filters or add a new player
                </p>
              </div>
            ) : (
              <>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Position</TableHead>
                      <TableHead>Club</TableHead>
                      <TableHead>Nationality</TableHead>
                      <TableHead>Age</TableHead>
                      <TableHead>Rating</TableHead>
                      <TableHead>Market Value</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {players.map((player) => (
                      <TableRow
                        key={player.id}
                        className="cursor-pointer hover:bg-gray-50"
                        onClick={() => router.push(`/dashboard/players/${player.id}`)}
                      >
                        <TableCell className="font-medium">
                          <div>
                            <div>{player.name}</div>
                            {player.full_name && player.full_name !== player.name && (
                              <div className="text-xs text-gray-500">{player.full_name}</div>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge className={getPositionColor(player.position)}>
                            {player.position}
                          </Badge>
                        </TableCell>
                        <TableCell>{player.current_club || '-'}</TableCell>
                        <TableCell>{player.nationality || '-'}</TableCell>
                        <TableCell>{player.age || '-'}</TableCell>
                        <TableCell>
                          {player.overall_rating ? (
                            <Badge variant="outline">{player.overall_rating}</Badge>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell className="font-medium">
                          {formatCurrency(player.market_value_eur)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>

                {/* Pagination */}
                <div className="flex items-center justify-between mt-6">
                  <div className="text-sm text-gray-500">
                    Showing {((pagination.page - 1) * pagination.per_page) + 1} to{' '}
                    {Math.min(pagination.page * pagination.per_page, pagination.total)} of{' '}
                    {pagination.total} players
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPagination((prev: PaginationMeta) => ({ ...prev, page: prev.page - 1 }))}
                      disabled={pagination.page === 1 || loading}
                    >
                      Previous
                    </Button>
                    <div className="flex items-center gap-2">
                      <span className="text-sm">
                        Page {pagination.page} of {pagination.total_pages}
                      </span>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPagination((prev: PaginationMeta) => ({ ...prev, page: prev.page + 1 }))}
                      disabled={pagination.page === pagination.total_pages || loading}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}