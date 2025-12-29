export interface Coach {
  id: string
  name: string
  full_name?: string
  current_club?: string
  nationality?: string
  date_of_birth?: string
  age?: number
  current_role: string
  preferred_formation: string
  coaching_level: string
  years_experience: number 
  estimated_salary_eur: number
  overall_rating?: number
  // potential_rating?: number
  scouting_notes?: string
  created_at: string
}

export interface CoachFilters {
  current_role?: string
  coaching_level?: string
  nationality?: string
  club?: string
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

export interface CoachesResponse {
  success: boolean
  data: Coach[]
  meta: {
    pagination: PaginationMeta
  }
}