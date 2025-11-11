import { Component, computed, inject, signal } from '@angular/core';
import { AdminService } from '../../services/admin.service';
import { CommonModule } from '@angular/common';
import { rxResource } from '@angular/core/rxjs-interop';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import Swal from 'sweetalert2';
import { NgChartsModule } from 'ng2-charts';
import { ChartConfiguration, ChartOptions } from 'chart.js';
import { AsignaturaCount, Ponderacion } from '@/auth/interfaces/adminResponse.interface';

type ViewType = 'populares' | 'afinidad' | 'probabilidad' | 'titulaciones' | 'configuracion';

@Component({
  selector: 'admin-page',
  imports: [CommonModule, FormsModule, NgChartsModule],
  templateUrl: './admin-page.component.html',
})
export class AdminPageComponent {
  private adminService = inject(AdminService);
  private router = inject(Router);

  currentView = signal<ViewType>('populares');
  isResetting = signal(false);

  selectedYear = signal<string | null>(null);

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

  getPonderacionesResource = rxResource({
    loader: () => this.adminService.getPonderaciones()
  })

  ponderaciones = computed<Ponderacion[]>(() => {
    const data = this.getPonderacionesResource.value();
    if (!data) return [];
    // Si vienen como tuplas [['2019-20',0.1], ...]
    return data as Ponderacion[];
  });


  // Configuración base para los gráficos
  chartOptions: ChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: true,
        position: 'right'
      }
    }
  };

  protected getChartData(data: AsignaturaCount[] | undefined | null) {
    if (!data || data.length === 0) {
      return {
        labels: [],
        datasets: [{
          label: 'No hay datos disponibles',
          data: [],
          backgroundColor: []
        }]
      };
    }

    return {
      labels: data.map(item => item.nombre || 'Sin nombre'),
      datasets: [{
        label: 'Número de consultas',
        data: data.map(item => item.count || 0),
        backgroundColor: [
          '#3b82f6',
          '#10b981',
          '#f59e0b',
          '#ef4444',
          '#8b5cf6'
        ].slice(0, data.length) // Asegurar que tenemos suficientes colores
      }]
    };
  }

  popularesChartData = signal<ChartConfiguration<'bar'>['data']>({
    labels: [],
    datasets: []
  });

  afinidadChartData = signal<ChartConfiguration<'pie'>['data']>({
    labels: [],
    datasets: []
  });

  probabilidadChartData = signal<ChartConfiguration<'doughnut'>['data']>({
    labels: [],
    datasets: []
  });

  titulacionesChartData = signal<ChartConfiguration<'bar'>['data']>({
    labels: [],
    datasets: []
  });
  // objeto plano para edición en template
  editingPonderacion: Ponderacion | null = null;

  // Map con los valores en edición (mutable)
  editingMap = signal<Record<string, number>>({});

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

// Validar y enviar todo de una vez
  guardarTodas() {
    const payload = this.editingMap();
    const años = Object.keys(payload);
    if (años.length === 0) {
      Swal.fire({ icon: 'info', title: 'Nada que guardar', text: 'No hay ponderaciones cargadas.' });
      return;
    }

    // Validaciones por elemento
    for (const y of años) {
      const v = payload[y];
      if (v == null || Number.isNaN(v)) {
        Swal.fire({ icon: 'error', title: 'Valor inválido', text: `Peso vacío o no numérico en ${y}` });
        return;
      }
      if (v < 0 || v > 1) {
        Swal.fire({ icon: 'error', title: 'Rango inválido', text: `El peso de ${y} debe estar entre 0 y 1.` });
        return;
      }
    }

    // Validación suma ≤ 1
    const suma = Object.values(payload).reduce((a, b) => a + Number(b), 0);
    if (suma > 1 + 1e-9 || suma < 1 - 1e-9) { // tolerancia numérica pequeña
      Swal.fire({ icon: 'error', title: 'Suma incorrecta', text: `La suma de los pesos es ${suma.toFixed(3)} (debe ser 1).` });
      return;
    }

    // Confirmación visual + envío
    Swal.fire({
      title: 'Confirmar cambios',
      html: `Vas a guardar ${años.length} ponderaciones. <br/>Suma actual: <b>${suma.toFixed(3)}</b>`,
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Guardar',
    }).then((res) => {
      if (!res.isConfirmed) return;

      // Preparar payload tipo {ponderaciones: [{year, peso}, ...]}
      const body = { ponderaciones: años.map(y => ({ year: y, peso: Number(payload[y]) })) };

      Swal.fire({ title: 'Guardando...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });

      this.adminService.setPonderaciones(body).subscribe({
        next: () => {
          Swal.fire({ icon: 'success', title: 'Guardadas', text: 'Todas las ponderaciones se han actualizado.' });
          // refrescar resource
          this.getPonderacionesResource.reload();
        },
        error: (err) => {
          const msg = err?.error?.detail ?? 'Error al guardar las ponderaciones';
          Swal.fire({ icon: 'error', title: 'Error', text: String(msg) });
        }
      });
    });
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
