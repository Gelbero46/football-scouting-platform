'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import ApiClient from '@/lib/api-client'
import { CoachFilters, Coach, PaginationMeta } from '@/lib/types/coach'
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

export default function CoachesPage() {
  const { getToken } = useAuth()
  const router = useRouter()
  
  const [coaches, setCoaches] = useState<Coach[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pagination, setPagination] = useState<PaginationMeta>({
    page: 1,
    per_page: 20,
    total: 0,
    total_pages: 0
  })
  
  // Filters
  const [filters, setFilters] = useState<CoachFilters>({
    search: '',
    current_role: '',
    club: '',
    sort_by: 'name',
    sort_order: 'asc'
  })

  const fetchCoaches = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const token = await getToken()
      const api = new ApiClient(token!)
      
      // Build query params
      const params = {
        skip: (pagination.page - 1) * pagination.per_page,
        limit: pagination.per_page,
        ...(filters.search && { search: filters.search }),
        ...(filters.current_role && filters.current_role != "*" && { current_role: filters.current_role }),
        ...(filters.club && { current_club: filters.club }),
        sort_by: filters.sort_by,
        sort_order: filters.sort_order
      }
      
      console.log("loading", loading, "params", params)
      const response = await api.coaches.list(params)
      
      console.log("response", response)
      setCoaches(response.data.data)
      setPagination(response.data.meta.pagination)
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch coaches')
      console.error('Error fetching coaches:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCoaches()
  }, [pagination.page, filters.sort_order])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    console.log("filters", filters)
    setPagination((prev: PaginationMeta) => ({ ...prev, page: 1 })) // Reset to page 1
    fetchCoaches()
  }

  const handleFilterChange = (key: keyof CoachFilters, value: string) => {
    setFilters((prev: CoachFilters) => ({ ...prev, [key]: value }))
  }

  const formatCurrency = (value?: number) => {
    if (!value) return 'N/A'
    if (value >= 1000000) return `€${(value / 1000000).toFixed(1)}M`
    if (value >= 1000) return `€${(value / 1000).toFixed(0)}K`
    return `€${value}`
  }

  const getRoleColor = (current_role: string) => {
    const colors: Record<string, string> = {
      'head_coach': 'bg-purple-100 text-purple-800',
      'assistant': 'bg-blue-100 text-blue-800',
      'youth_coach': 'bg-green-100 text-green-800',
    }
    return colors[current_role] || 'bg-gray-100 text-gray-800'
  }

  if (loading && coaches.length === 0) {
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
            <h1 className="text-3xl font-bold">coaches</h1>
            <p className="text-gray-500 mt-1">
              {pagination.total} coaches in database
            </p>
          </div>
          <Link href="/dashboard/coaches/new">
            <Button className="cursor-pointer">Add coach</Button>
          </Link>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Filters</CardTitle>
            <CardDescription>Search and filter coaches</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSearch} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Search */}
                <div className="md:col-span-2">
                  <Input
                    placeholder="Search by name or current_club..."
                    value={filters.search}
                    onChange={(e) => handleFilterChange('search', e.target.value)}
                  />
                </div>

                {/* current_role Filter */}
                <div className="justify-center text-center c">
                     <Select
                      value={filters.current_role}
                      onValueChange={(value: any) => handleFilterChange('current_role', value)}
                    >
                      <SelectTrigger className="cursor-pointer">
                        <SelectValue placeholder="current_role" />
                      </SelectTrigger>
                      <SelectContent className="cursor-pointer">
                        <SelectItem value="*">All current_roles</SelectItem>
                        <SelectItem value="head_coach">Head Coach</SelectItem>
                        <SelectItem value="assistant">Assistant</SelectItem>
                        <SelectItem value="youth_coach">Youth Coach</SelectItem>
                        {/* <SelectItem value="FW">Forward</SelectItem>
                        <SelectItem value="ST">Striker</SelectItem>
                        <SelectItem value="LW">Left Wing</SelectItem>
                        <SelectItem value="RW">Right Wing</SelectItem> */}
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
                      current_role: '',
                      club: '',
                      sort_by: 'name',
                      sort_order: 'asc'
                    })
                    fetchCoaches()
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

        {/* coaches Table */}
        <Card>
          <CardHeader>
            <CardTitle>All coaches</CardTitle>
            <CardDescription>
              Click on a coach to view details
            </CardDescription>
          </CardHeader>
          <CardContent>
            {coaches.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No coaches found</p>
                <p className="text-gray-400 text-sm mt-2">
                  Try adjusting your filters or add a new coach
                </p>
              </div>
            ) : (
              <>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>current_role</TableHead>
                      <TableHead>current_club</TableHead>
                      <TableHead>Nationality</TableHead>
                      <TableHead>Age</TableHead>
                      <TableHead>Level</TableHead>
                      <TableHead>Market Value</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {coaches.map((coach) => (
                      <TableRow
                        key={coach.id}
                        className="cursor-pointer hover:bg-gray-50"
                        onClick={() => router.push(`/dashboard/coaches/${coach.id}`)}
                      >
                        <TableCell className="font-medium">
                          <div>
                            <div>{coach.name}</div>
                            {coach.full_name && coach.full_name !== coach.name && (
                              <div className="text-xs text-gray-500">{coach.full_name}</div>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge className={getRoleColor(coach.current_role)}>
                            {coach.current_role}
                          </Badge>
                        </TableCell>
                        <TableCell>{coach.current_club || '-'}</TableCell>
                        <TableCell>{coach.nationality || '-'}</TableCell>
                        <TableCell>{coach.age || '-'}</TableCell>
                        <TableCell>
                          {coach.coaching_level ? (
                            <Badge variant="outline">{coach.coaching_level}</Badge>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell className="font-medium">
                          {formatCurrency(coach.estimated_salary_eur)}
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
                    {pagination.total} coaches
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