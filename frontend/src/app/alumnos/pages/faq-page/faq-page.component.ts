import { AdminService } from '@/auth/services/admin.service';
import { Component, inject } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-faq-page',
  imports: [],
  templateUrl: './faq-page.component.html',
})
export class FaqPageComponent {

  adminService = inject(AdminService);

  //Carga las ponderaciones desde el backend.
  getPonderacionesResource = rxResource({
    loader: () => this.adminService.getPonderaciones()
  })
}
