import { ChangeDetectionStrategy, Component } from '@angular/core';
import { TextInputComponent } from "@alumnos/components/text-input/text-input.component";

@Component({
  selector: 'app-main-page',
  imports: [TextInputComponent],
  templateUrl: './main-page.component.html',
})
export class MainPageComponent { }
