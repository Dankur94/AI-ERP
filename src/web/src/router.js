import { createRouter, createWebHistory } from 'vue-router'
import UploadView from './views/UploadView.vue'
import InvoiceView from './views/InvoiceView.vue'
import SearchView from './views/SearchView.vue'
import MatchView from './views/MatchView.vue'
import ReportView from './views/ReportView.vue'
import AlertView from './views/AlertView.vue'

const routes = [
  {
    path: '/',
    name: 'upload',
    component: UploadView,
  },
  {
    path: '/search',
    name: 'search',
    component: SearchView,
  },
  {
    path: '/matches',
    name: 'matches',
    component: MatchView,
  },
  {
    path: '/reports',
    name: 'reports',
    component: ReportView,
  },
  {
    path: '/alerts',
    name: 'alerts',
    component: AlertView,
  },
  {
    path: '/invoice/:id',
    name: 'invoice',
    component: InvoiceView,
    props: true,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
