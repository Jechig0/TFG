import { Component, inject, signal } from '@angular/core';
import { AdminService } from '../../services/admin.service';
import { CommonModule } from '@angular/common';
import { rxResource } from '@angular/core/rxjs-interop';

type ViewType = 'populares' | 'afinidad' | 'probabilidad' | 'titulaciones';

@Component({
  selector: 'admin-page',
  imports: [CommonModule],
  templateUrl: './admin-page.component.html',
})
export class AdminPageComponent {
  private adminService = inject(AdminService);
  
  currentView = signal<ViewType>('populares');

  asignaturasPopularesResource = rxResource({
    loader: () => this.adminService.getAsignaturasPopulares()
  });

  asignaturasAfinidadResource = rxResource({
    loader: () => this.adminService.getAsignaturasAfinidad()
  });

  asignaturasProbabilidadResource = rxResource({
    loader: () => this.adminService.getAsignaturasProbabilidad()
  });

  titulacionesResource = rxResource({
    loader: () => this.adminService.getTitulaciones()
  });

  setView(view: ViewType) {
    this.currentView.set(view);
  }
}