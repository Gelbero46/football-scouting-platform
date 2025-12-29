export interface Player {
  id: string
  name: string
  full_name?: string
  position: string
  current_club?: string
  nationality?: string
  date_of_birth?: string
  age?: number
  height_cm?: number
  weight_kg?: number
  preferred_foot?: string
  market_value_eur?: number
  overall_rating?: number
  potential_rating?: number
  scouting_notes?: string
  created_at: string
}

export interface PlayerFilters {
  position?: string
  club?: string
  nationality?: string
  min_value?: number
  max_value?: number
  search?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface PaginationMeta {
  page: number
  per_page: number
  total: number
  total_pages: number
}

export interface PlayersResponse {
  success: boolean
  data: Player[]
  meta: {
    pagination: PaginationMeta
  }
}