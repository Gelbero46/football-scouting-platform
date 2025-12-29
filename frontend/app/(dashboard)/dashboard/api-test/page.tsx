'use client'

import { useAuth } from '@clerk/nextjs'
import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function ApiTestPage() {
  const { getToken } = useAuth()
  const [token, setToken] = useState<string>('')
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    const fetchToken = async () => {
      const t = await getToken()
      setToken(t || '')
    }
    fetchToken()
  }, [getToken])

  const copyToken = () => {
    navigator.clipboard.writeText(token)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">API Testing</h1>
        
        <Card>
          <CardHeader>
            <CardTitle>Your Authentication Token</CardTitle>
            <CardDescription>
              Copy this token to use in Swagger UI (http://localhost:8000/docs)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-100 p-4 rounded-lg mb-4 break-all font-mono text-sm">
              {token || 'Loading...'}
            </div>
            <Button onClick={copyToken} disabled={!token}>
              {copied ? '✓ Copied!' : 'Copy Token'}
            </Button>
          </CardContent>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>How to use Swagger UI</CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="list-decimal list-inside space-y-2">
              <li>Copy the token above</li>
              <li>Visit <a href="http://localhost:8000/docs" target="_blank" className="text-blue-600 underline">http://localhost:8000/docs</a></li>
              <li>Click the green "Authorize" button</li>
              <li>In the "Value" field, paste: <code className="bg-gray-100 px-2 py-1 rounded">Bearer YOUR_TOKEN</code></li>
              <li>Click "Authorize", then "Close"</li>
              <li>Now you can test all API endpoints!</li>
            </ol>
          </CardContent>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Sample Data to Add</CardTitle>
            <CardDescription>Use these examples in Swagger UI</CardDescription>
          </CardHeader>
          <CardContent>
            <h3 className="font-semibold mb-2">Player 1 - Erling Haaland</h3>
            <pre className="bg-gray-100 p-4 rounded-lg text-sm overflow-x-auto mb-4">
{`{
  "name": "Erling Haaland",
  "full_name": "Erling Braut Haaland",
  "position": "ST",
  "current_club": "Manchester City",
  "nationality": "Norway",
  "date_of_birth": "2000-07-21",
  "height_cm": 194,
  "weight_kg": 88,
  "preferred_foot": "left",
  "market_value_eur": 180000000,
  "overall_rating": 91,
  "potential_rating": 94
}`}
            </pre>

            <h3 className="font-semibold mb-2">Player 2 - Kylian Mbappé</h3>
            <pre className="bg-gray-100 p-4 rounded-lg text-sm overflow-x-auto mb-4">
{`{
  "name": "Kylian Mbappé",
  "full_name": "Kylian Mbappé Lottin",
  "position": "LW",
  "current_club": "Real Madrid",
  "nationality": "France",
  "date_of_birth": "1998-12-20",
  "height_cm": 178,
  "weight_kg": 73,
  "preferred_foot": "right",
  "market_value_eur": 200000000,
  "overall_rating": 93,
  "potential_rating": 95
}`}
            </pre>

            <h3 className="font-semibold mb-2">Coach - Pep Guardiola</h3>
            <pre className="bg-gray-100 p-4 rounded-lg text-sm overflow-x-auto">
{`{
  "name": "Pep Guardiola",
  "full_name": "Josep Guardiola i Sala",
  "current_club": "Manchester City",
  "current_role": "head_coach",
  "nationality": "Spain",
  "date_of_birth": "1971-01-18",
  "preferred_formation": "4-3-3",
  "coaching_level": "elite",
  "overall_rating": 95
}`}
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}