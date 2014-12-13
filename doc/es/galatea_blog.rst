.. inheritref:: galatea_blog/galatea:section:blog

----
Blog
----

Esta App dispone la funcionalidad de la generación de un blog: artículos o posts.
El sistema de blog le permite publicar contenidos que se muestran en formato listado
siendo el más reciente el primero de la lista.

Además, cada blog puede disponer de comentarios que pueden publicar los usuarios
(o los usuarios).

.. inheritref:: galatea_blog/galatea:section:post

Post
----

Para la gestión de posts o artículos accede a |menu_galatea_blog|. Como todo registro
web deberá tener en cuenta:

* Slug: Es el ID o clave del vuestro registro. Sólo debe usar los carácteres az09-
  (sin acentos ni espacios). Este campo debe ser único ya que no pueden haber más
  de dos o más slugs en su blog. Recuerde que es un campo multi idioma.
  Cuando introduzca un título se le propone un slug a partir del título que después
  lo podrá cambiar. Un slug podría ser 'mi-articulo-sobre-tryton' y crearia una dirección como
  http://www.midominio.com/es/blog/post/mi-articulo-sobre-tryton
* SEO MetaKeyword. Introduce palabras clave de su artículo separados por comas
  (no más de 155 carácteres) que se usará para los buscadores. Un ejemplo de MetaKeyword
  podría ser "tryton,documentación,web,blog". Recuerde que es un campo multi idioma.
* SEO MetaDescription. Introduce una descripción breve del artículo (el resumen)
  (no más de 155 carácteres) que se usará para los buscadores. Un ejemplo de MetaDescription
  podria ser "Mi primer artículo sobre la experiencia de Tryton". Recuerde que es un
  campo multi idioma.
* SEO MetaTitle. Si el título del artículo en los buscadores desea que sea diferente del nombre
  del artículo puede usar este campo para cambiarlo. Recuerde que es un campo multi idioma.

Para el contenido de un blog puede usar los campos descripciones. Usa el campo "Descripción larga"
para posts con contenido extenso. Para el formato HTML usa los tags de Wiki para dar formato a su contendido.
Los tags de wiki le permite formatear el texto para después sea mostrado con HTML. Para
información de los tags de wiki puede consultar `MediaWiki <http://meta.wikimedia.org/wiki/Help:Editing>`_

Como siempre recuerde que si edita un post o artículo y su web es multi idioma, debe de cambiar
el contenido por cada idioma con el campo de la "bandera".

En el post podemos añadir adjuntos. Para acceder a los adjuntos puede realizar un vínculo al fichero
publicado:

    /file/nombre-del-fichero.jpg

Si desea publicar una imagen en el cuerpo del post, consulte la documentación de `MediaWiki.
Rendering a single image <http://www.mediawiki.org/wiki/Help:Images#Rendering_a_single_image>`_ 

.. important:: Si cambia el nombre del post o artículo, el slug se volverá a generar.
              Debe tener cuidado con esta acción pues si su página ya está indexada
              por los buscadores y cambia las urls o slugs, estas páginas ya no se van
              a encontrar y devolverá el "Error 404. Not Found". En el caso que desea cambiar
              las url's contacte con el administrador para que le active las redirecciones
              y evitar páginas no encontradas.

Para acceder a un post en concreto accede a:

* Español: http://www.midominio.com/es/blog/<SLUG>
* Catalan: http://www.midominio.com/ca/blog/<SLUG>
* Inglés: http://www.midominio.com/en/blog/<SLUG>

.. inheritref:: galatea_blog/galatea:section:todos_posts

Todos los posts
---------------

Como todo blog dispone de un listado de todos los posts o artículos publicados. Estos siempre
se listaran por fecha de creación por orden descendiente.

Para acceder a todos los posts o artículos accede a http://www.sudominio.com/es/blog/

También podemos hacer una búsqueda simple por el nombre completo
(rec_name: por defecto nombre):

* Español: http://www.midominio.com/es/blog/?q=TEXTO
* Catalan: http://www.midominio.com/ca/blog/?q=TEXTO
* Inglés: http://www.midominio.com/en/blog/?q=TEXTO

En este ejemplo "TEXTO" equivale la cadena de texto que se usaria para buscar.

.. inheritref:: galatea_blog/galatea:section:buscar

Buscar
------

En el caso que nuestro sitio web se haya configurado el motor de búsqueda o indexación
podemos usar la url de buscar en nuestros productos.

* Español: http://www.midominio.com/es/blog/search/
* Catalan: http://www.midominio.com/ca/blog/search/
* Inglés: http://www.midominio.com/en/blog/search/

Podemos cancatenar palabras usando "+" para AND y el "-" para el NOT. En el caso
que sean espacios, se reemplazan como "+" (AND).

Para el uso de Whoosh como la creación de esquemas e indexación consulte la documentación
del módulo Whoosh.

.. inheritref:: galatea_blog/galatea:section:comentarios

Comentarios
-----------

Si a la configuración global está activo los usuarios podrán añadir comentarios en sus posts.
Si en un post no desea que se publiquen comentarios, desactive la opción de "Comentarios".

Si desea que un comentario desactivar y no se publique, puede desactivar la opción de activo.

.. |menu_galatea_blog| tryref:: galatea_blog.menu_galatea_blog/complete_name
