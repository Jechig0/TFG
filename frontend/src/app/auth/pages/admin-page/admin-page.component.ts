import { Component, inject, signal } from '@angular/core';
import { AdminService } from '../../services/admin.service';
import { CommonModule } from '@angular/common';
import { rxResource } from '@angular/core/rxjs-interop';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import Swal from 'sweetalert2';

type ViewType = 'populares' | 'afinidad' | 'probabilidad' | 'titulaciones' | 'configuracion';

@Component({
  selector: 'admin-page',
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-page.component.html',
})
export class AdminPageComponent {
  private adminService = inject(AdminService);
  private router = inject(Router);

  currentView = signal<ViewType>('populares');
  isResetting = signal(false);

  // Ponderaciones
  ponderaciones = {
    expediente: 0.4,
    historial: 0.3,
    demanda: 0.3
  };

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

  async resetClusters() {
    Swal.fire({
      title: 'Reiniciar Clusters',
      text: '¿Está seguro de que desea reiniciar los clusters? Esta operación puede tardar varios minutos.',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Confirmar',
      cancelButtonText: 'Cancelar'
    }).then((result) => {
      if (result.isConfirmed) {
        this.isResetting.set(true);
        this.adminService.resetClusters().subscribe({
          next: () => {
            Swal.fire('Éxito', 'Los clusters han sido reiniciados', 'success');
          },
          error: () => {
            Swal.fire('Error', 'No se pudieron reiniciar los clusters', 'error');
          },
          complete: () => {
            this.isResetting.set(false);
          }
        });
      }
    });
  }

  async updatePonderaciones() {
    if (this.ponderaciones.expediente + this.ponderaciones.historial + this.ponderaciones.demanda !== 1) {
      alert('La suma de las ponderaciones debe ser 1');
      return;
    }

    try {
      await this.adminService.setPonderaciones(this.ponderaciones).toPromise();
      alert('Ponderaciones actualizadas correctamente');
    } catch (error) {
      alert('Error al actualizar las ponderaciones');
    }
  }

  logout() {
    Swal.fire({
          title: 'Cerrar sesión',
          text: 'Pulsa Confirmar para cerrar sesión.',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Confirmar',
          cancelButtonText: 'Cancelar'
    }).then((result) => {
      if (result.isConfirmed) {
        sessionStorage.removeItem('isAdmin');
        this.router.navigate(['/']);
      }
    });
    ;
  }
}
