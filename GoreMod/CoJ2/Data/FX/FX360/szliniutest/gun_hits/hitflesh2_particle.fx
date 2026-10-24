ParticleDef()
{
	LifeTime()
	{
		keyf(0, 1.2)
	}

	GravityMul()
	{
		keyf(0, 3.4)
	}

	Drag()
	{
		keyf(0, 2)
	}

	WindInfluence()
	{
		keyf(0, 0.3)
	}

	Color()
	{
		keyv4(0.003393, 0.639443, 0.643364, 0.643364, 0.997315)
		keyv4(0.852346, 0.627504, 0.626211, 0.631769, 0.795048)
		keyv4(1.489640, 0.619835, 0.627678, 0.608071, -0.105227)
	}
	
	Size()
	{
		randf(-0.002542, 13.553656, 23.382532)
		randf(0.485465, 4.002180, 7.522155)
		randf(1.502142, -0.005779, -0.005779)
	}

	Rotation()
	{
		randf(0, 20, 360)
	}

	Align("always") //Align("on_start")
	
	//AspectRatio()
	//{
		//keyf(0.000000, 0.700000)
	//}

	Material("bloodsmall_particleblend.mat", "bloodsmall_particleblend.mat")

	TexMultiRect(2, 2, 4)

	TexPlayMode("random_once", 1.000000)  //TexPlayMode("forward", 20) //TexPlayMode("forward_loop", 21.000000) //TexStartMode("random")	

	

}

