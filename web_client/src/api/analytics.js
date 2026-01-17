import request from './index'

export function getClassTrend(classId) {
  return request.get(`/analytics/class_trend/${classId}`)
}

export function getAbsentRanking(classId) {
  return request.get(`/analytics/absent_ranking/${classId}`)
}