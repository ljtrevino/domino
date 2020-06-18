# Domino Image Creator

## Running the application
This project uses Python 3

After you cd into the domino folder, run the following command with the filepath of the image you want to use (i.e. `images/paddington.png`):  
- `$ python main.py <filepath>`

If you do not have kivy installed or updated to version 1.11.1, you can run:  
- `$ python -m pip install --upgrade pip wheel setuptools`  
- `$ python -m pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew --extra-index-url https://kivy.org/downloads/packages/simple/`  
- `$ python -m pip install kivy==1.11.1`  

If you do not have PIL or Numpy installed, you can run:
- `$ python -m pip install pillow` 
- `$ python -m pip install numpy` 

## Using the application
The image from the filepath you provided will show up on the left side of the screen.  In the center of the screen will be a pixelated version of that image.  Drag the slider to increase or decrease pixelation, which corresponds to the number of dominoes that will be used to generate the final piece (where each pixel represents a single side of a double-nine domino).

The toggle in the top-right corner allows you to toggle between using white dominoes or using black dominoes.  When white dominoes are selected, the GUI background will be lighter.  Likewise, when black dominoes are selected, the GUI background will be darker.

Once you have positioned the slider to the location of your choice, click the generate button.  A preview of the output image will appear on the right side of the screen once the generation is complete.  It may take a minute or two to generate the output, especially for images with more pixels / more sets of dominoes.

Once the output has been generated, a higher-quality version of the output domino image will be saved to the `output` folder as "`<filename>`\_`<number of domino sets>`\_domino_sets_`<black|white>`.png"

## Examples

Original Image             |  Domino Image (Black)     |  Domino Image (White)     |  Number of Domino Sets
:-------------------------:|:-------------------------:|:-------------------------:|:-------------------------:
![](https://lh3.googleusercontent.com/s8Cb86kUjjMJPneVpOYLFzdfgszLhxfgKYKcVSYeDnC-_8OGzX9SqbiU0YE-Pif0yF_RbmAL-sqYnA0l6Mz1nqPhWEhwQjFdUiae1-5vxzmcF_szWDpOR4UNOepH_kKhHX3DPNY80A=w2400)  |  ![](https://lh3.googleusercontent.com/7OlmkRVlK4hmp2Bm_-w3AK6wkMF7YPBalg-8FIzLMhRl6Kjj6mgAbUu5DegOeiWw1NaiTHIhzFKQkE8mBvA_v6uEIgzdbnbibqhGnpguf092YrGHrMQUfzJZrVcMjlMCQ_rCLwtJng=w2400)  |  ![](https://lh3.googleusercontent.com/sfbUVHKTJVXvKgczoIGlGKd0SFMDwZ9Yy66sBuwe0an82cIt7Zzx2GlsT8CmD7GSCEuHpTXVGdYZn5nTkGOOmiCelF1vfKqbZUMn5AulmTy9dLCMP7eAlqOlDq6sVrtbx1Mpgvi0og=w2400)   |   42
![](https://lh3.googleusercontent.com/Pa_TQptd3RftCQM5tCFJ3iN8G5_4jnNQqa1R-0Krey3dKy08AHC2k9hXeWYHzzqkC8OVeTsESiw53EC87TVlGBDUhYDwPdlvxZWQ2KUiGqDs5Cj6rz9u1MvHF_2UFlZU0TAY_Uugjg=w2400)  |  ![](https://lh3.googleusercontent.com/Y74MONLtHyglqBpKzuUeInZX3L9pr85p6IieLx_NIh20KvO7wU30JzIJTe5CYPqyo4QvUYIyRoS5VpsFYb6RjMyaGdJP0f8db07AHkkdAIzAedBpSC9QnpAWPrSpQ95rpuVIJDqlTQ=w2400)  |  ![](https://lh3.googleusercontent.com/OIbEhN12FmWjilUShzy_6Z-h5sqx3ptZZ3nXZAkfdUaWesF0vXcrjr_2B5CANhC8GDGlMfR714K_JZE0ZVy6fYbCTu4yDRlHe1ptHqFgPG5caD5qbq0yjxBiEoVrf7dgvTbogQ6lNQ=w2400)   |   48
![](https://lh3.googleusercontent.com/0AscBsaj2qafwjhWJmDAGtgi9fdYoDYz19HaNCrIUY1k_TRlHr-7o_lCXWMiH0PvR74W2979kTo0M4D_VYEWKH3mrphtlQkmZcx98fKr_zfrVCI8ZUg9f0zErGNRE8YqJv16pf3PJQ=w2400)  |  ![](https://lh3.googleusercontent.com/AmPYX5owYlQ6Z8rU8P7Gf6PgviXWok4Qxn-eyHPmp44cFcYV1y6QHeruswxkufq78fNOzqgbJdHEA5UHwSiqai5-lkbOCCFXuS6_Dv3BpXvYcFTv50jopecFuG6NdkWKK2UDSEre5g=w2400)  |  ![](https://lh3.googleusercontent.com/myMR2mGsUC-7KnRerpKGPfCdcRx5Lmg26d5mm9DciDhPpS6eXsbTcIP1AdVrWLu_1zfoNgzCpKXI7VaxtWWyJ7r2O_--ql0wrSDAia6hRYCrVlWolLw9eoIKJOIT5Gi1P9P_y-HuXg=w2400)   |   55
