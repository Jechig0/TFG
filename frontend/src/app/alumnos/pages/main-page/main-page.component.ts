import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { TextInputComponent } from "@alumnos/components/text-input/text-input.component";
import { Router } from '@angular/router';

@Component({
  selector: 'app-main-page',
  imports: [TextInputComponent],
  templateUrl: './main-page.component.html',
})
export class MainPageComponent { 

  router = inject(Router);

    goToInsert() {
      this.router.navigate([`/nuevo-alumno`])
  } 
}
