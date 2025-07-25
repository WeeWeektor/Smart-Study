import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from './index'
import React from 'react'

interface AuthCardProps {
  title: string
  description?: string
  children: React.ReactNode
}

export const AuthCard: React.FC<AuthCardProps> = ({
  title,
  description,
  children,
}) => (
  <Card className="border-slate-200 shadow-lg max-w-md mx-auto">
    <CardHeader className="space-y-1">
      <CardTitle className="text-2xl text-center text-slate-900">
        {title}
      </CardTitle>
      {description && (
        <CardDescription className="text-center">{description}</CardDescription>
      )}
    </CardHeader>
    <CardContent>{children}</CardContent>
  </Card>
)
