EmiterDef()
{
	LifeTime()
	{
		keyf(0, 1.5)
	}

	GenType("one_time")

	NumParticles()
	{
		randf(0, 2, 4)
	}

	StartVelocity()
	{
		keyf(0, 255)
	}

	StartVelocityRand()
	{
		keyv(0, 240, 0, 240)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")
}
